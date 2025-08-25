# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "lxml>=5.2.0",
#     "httpx>=0.27.0",
# ]
# ///
"""
Extract all images from an SVG.

- Embedded data URLs:   data:image/*;base64,<payload>
- External refs:        <image>/<feImage> href|xlink:href and CSS url(...)
  * http(s) fetched with httpx (follow redirects)
  * file paths resolved relative to the SVG

Default output & naming:
  - Output directory defaults to the current working directory (" . ").
  - If exactly one image was extracted, save as:  <svg_stem>.<ext>
  - If multiple images were extracted, save as:   <svg_stem>_01.<ext>, <svg_stem>_02.<ext>, ...

Usage:
  uv run extract_svg_images.py input.svg [-o OUTDIR] [--skip-external] [--dedupe] [--verbose]

Notes:
  - Handles URL-encoded base64 and whitespace/newlines within payloads
  - Supports common raster types (png, jpg, gif, webp, bmp, tiff, ico, avif, heic) and vector (svg+xml)
  - Detects .svgz (gzip) automatically
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import re
import sys
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple

import httpx
from lxml import etree


MIME_TO_EXT = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/bmp": "bmp",
    "image/tiff": "tif",
    "image/x-icon": "ico",
    "image/vnd.microsoft.icon": "ico",
    "image/avif": "avif",
    "image/heic": "heic",
    "image/svg+xml": "svg",
}


def guess_ext_from_mime(mime: str) -> str:
    m = (mime or "").lower().split(";", 1)[0].strip()
    if m in MIME_TO_EXT:
        return MIME_TO_EXT[m]
    if m.startswith("image/"):
        return m.replace("image/", "").replace("+xml", "")
    return "bin"


def sanitize_base64(b64: str) -> str:
    # Decode URL-escapes (%2B etc.) then remove whitespace/newlines
    return urllib.parse.unquote(b64).replace("\n", "").replace("\r", "").replace(" ", "")


def read_svg_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    # gzip magic: 1f 8b
    if len(data) >= 2 and data[0] == 0x1F and data[1] == 0x8B:
        return gzip.decompress(data)
    return data


def find_data_urls(text: str) -> List[Tuple[str, str]]:
    """
    Return list of (mime, payload_base64) tuples for image data URLs anywhere in text.
    """
    pattern = re.compile(
        r"data:(image/[a-z0-9.+-]+)(;[^,]*?)?;base64,([a-z0-9+/=%\s]+)",
        re.I,
    )
    results: List[Tuple[str, str]] = []
    seen: Set[str] = set()
    for m in pattern.finditer(text):
        whole = m.group(0)
        if whole in seen:
            continue
        seen.add(whole)
        mime = m.group(1)
        payload = m.group(3)
        results.append((mime, payload))
    return results


def extract_css_urls(css_text: str) -> Set[str]:
    urls = set()
    for m in re.finditer(r"url\(\s*(['\"]?)([^'\"\)]+)\1\s*\)", css_text, flags=re.I):
        urls.add(m.group(2))
    return urls


def find_external_refs(svg_text: str, root: etree._Element) -> Set[str]:
    """
    Gather candidate external refs from <image>/<feImage> href/xlink:href and CSS url(...).
    Excludes data: URLs (handled separately).
    """
    refs: Set[str] = set()

    # XML attributes on elements
    for el in root.xpath(".//*[local-name()='image' or local-name()='feImage']"):
        href = el.get("href") or el.get("{http://www.w3.org/1999/xlink}href")
        if href and not href.startswith("data:"):
            refs.add(href)

        # style attribute might contain url(...)
        style_attr = el.get("style")
        if style_attr:
            refs.update(extract_css_urls(style_attr))

    # CSS blocks and anywhere in text
    for url in extract_css_urls(svg_text):
        if not url.startswith("data:"):
            refs.add(url)

    # Keep only image-looking ones or remote URLs (we'll check content-type later)
    def likely(p: str) -> bool:
        return bool(re.search(r"\.(png|jpe?g|gif|webp|bmp|tiff?|ico|svg)$", p, re.I))

    refs = {r for r in refs if r.startswith(("http://", "https://", "file://")) or likely(r)}
    return refs


@dataclass
class ImageItem:
    data: bytes
    ext: str
    source: str  # description (e.g., "embedded #3", URL, or path)


def decode_data_urls(pairs: Iterable[Tuple[str, str]], dedupe: bool, verbose: bool) -> List[ImageItem]:
    items: List[ImageItem] = []
    seen_hashes: Set[str] = set()

    for idx, (mime, payload) in enumerate(pairs):
        ext = guess_ext_from_mime(mime)
        b64 = sanitize_base64(payload)
        try:
            blob = base64.b64decode(b64, validate=False)
        except Exception as e:
            if verbose:
                print(f"[warn] failed to base64-decode {mime}: {e}", file=sys.stderr)
            continue

        if dedupe:
            h = hashlib.sha256(blob).hexdigest()
            if h in seen_hashes:
                if verbose:
                    print(f"[skip] duplicate embedded image (sha256 {h[:12]}...)")
                continue
            seen_hashes.add(h)

        items.append(ImageItem(blob, ext, f"embedded #{idx}"))

    return items


def fetch_or_copy_external(
    svg_dir: Path, refs: Iterable[str], dedupe: bool, verbose: bool
) -> List[ImageItem]:
    items: List[ImageItem] = []
    seen_hashes: Set[str] = set()

    for ref in refs:
        try:
            if ref.startswith(("http://", "https://")):
                with httpx.Client(follow_redirects=True, timeout=20.0) as client:
                    r = client.get(ref)
                r.raise_for_status()
                ct = (r.headers.get("content-type") or "").split(";", 1)[0].strip()
                ext = guess_ext_from_mime(ct) if ct.startswith("image/") else "bin"

                # Try to refine ext from URL path if available
                try:
                    name = Path(urllib.parse.urlparse(ref).path).name
                    if name and "." in name:
                        maybe_ext = name.rsplit(".", 1)[-1].lower()
                        if maybe_ext:
                            ext = maybe_ext
                except Exception:
                    pass

                blob = r.content

            elif ref.startswith("file://"):
                p = Path(urllib.parse.urlparse(ref).path)
                blob = p.read_bytes()
                ext = (p.suffix.lstrip(".") or "bin").lower()

            else:
                # local path (absolute or relative to SVG)
                p = Path(ref)
                if not p.is_absolute():
                    p = (svg_dir / ref).resolve()
                blob = p.read_bytes()
                ext = (p.suffix.lstrip(".") or "bin").lower()

            if dedupe:
                h = hashlib.sha256(blob).hexdigest()
                if h in seen_hashes:
                    if verbose:
                        print(f"[skip] duplicate external image (sha256 {h[:12]}...)")
                    continue
                seen_hashes.add(h)

            items.append(ImageItem(blob, ext, ref))

        except Exception as e:
            if verbose:
                print(f"[warn] failed to fetch/copy {ref!r}: {e}", file=sys.stderr)

    return items


def parse_args(argv: List[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Extract images from an SVG.")
    ap.add_argument("input_svg", help="Path to SVG or SVGZ")
    ap.add_argument(
        "-o",
        "--outdir",
        default=".",  # default: current directory
        help="Output directory (default: current directory)",
    )
    ap.add_argument("--skip-external", action="store_true", help="Only extract embedded data: URLs")
    ap.add_argument("--dedupe", action="store_true", help="Dedupe identical images by content hash")
    ap.add_argument("--verbose", action="store_true", help="Verbose output")
    return ap.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    in_path = Path(args.input_svg).expanduser().resolve()
    out_dir = Path(args.outdir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        print(f"error: input not found: {in_path}", file=sys.stderr)
        return 2

    raw = read_svg_bytes(in_path)
    text = raw.decode("utf-8", "ignore")

    # Parse XML (robust to namespaces)
    try:
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(raw, parser=parser)
    except Exception as e:
        print(f"[warn] XML parse failed, continuing with regex-only: {e}", file=sys.stderr)
        root = None  # type: ignore

    # Collect ALL images first (so we can decide naming based on total count)
    images: List[ImageItem] = []

    # Embedded
    pairs = find_data_urls(text)
    images.extend(decode_data_urls(pairs, dedupe=args.dedupe, verbose=args.verbose))

    # External
    if not args.skip_external:
        refs = find_external_refs(text, root) if root is not None else extract_css_urls(text)
        refs = {r for r in refs if not r.startswith("data:")}
        images.extend(fetch_or_copy_external(in_path.parent, refs, dedupe=args.dedupe, verbose=args.verbose))

    total = len(images)
    if total == 0:
        print("No images found.")
        return 0

    # Naming scheme
    stem = in_path.stem
    pad = max(2, len(str(total))) if total > 1 else 0

    written_paths: List[Path] = []
    for i, item in enumerate(images, start=1):
        if total == 1:
            name = f"{stem}.{item.ext}"
        else:
            name = f"{stem}_{i:0{pad}d}.{item.ext}"
        out_path = out_dir / name
        out_path.write_bytes(item.data)
        written_paths.append(out_path)
        if args.verbose:
            print(f"[save] {out_path} ({len(item.data)} bytes) from {item.source}")

    print(
        f"\nDone.\n"
        f"  Images saved: {total}\n"
        f"  Output dir  : {out_dir}\n"
    )
    if args.verbose:
        for p in written_paths:
            print(f"  - {p}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

