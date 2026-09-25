# DevImage

**DevImage** is a fast, offline-first desktop image toolbox tailored for software engineers, designers, and technical creators.

Built with Python 3.12+ (PySide6 / Qt Quick QML).

## Features
- **Image Tools**: Resize, Compress, Convert, Crop, Watermark, Background Removal.
- **Developer Tools**: Image Inspector, Color Picker, OCR, Batch Rename, Copy Path.
- **AI Tools**: Local ONNX models + optional Gemini API integration.

## Development Setup

```bash
# Create virtual environment and install dependencies
uv venv
uv pip install -e ".[dev]"

# Run tests
uv run pytest tests/ -v

# Run lint checks
uv run ruff check src/ tests/

# Launch application
uv run devimage
```
