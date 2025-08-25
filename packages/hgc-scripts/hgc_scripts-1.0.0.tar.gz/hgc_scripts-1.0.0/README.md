# HGC Utility Scripts

A collection of utility scripts for HGC operations and tasks.

## Installation & Usage

### Published Package (PyPI)
```bash
# Run without installing
uvx hgc-scripts <script-name> [options]

# Install globally
uv tool install hgc-scripts
```

### Local Development
```bash
# Run scripts directly with dependencies
uv run scripts/<script_name>.py [options]

# Install locally in development mode
uv pip install -e .
<script-name> [options]

# Run via uvx from local directory
uvx --from . <script-name> [options]
```

## Available Scripts

| Script | Description | Documentation |
|--------|-------------|---------------|
| `svg-extract-images` | Extract embedded and external images from SVG files | [docs/svg-extract-images.md](docs/svg-extract-images.md) |

## Development

- Python 3.13+
- Per-script dependencies defined in PEP 723 script metadata
- Built with `uv` for fast dependency management

### Publishing
```bash
uv build
uv publish
```