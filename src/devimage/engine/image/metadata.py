"""Image metadata extraction using Pillow."""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from devimage.app.logging import get_logger
from devimage.core.errors import FileNotFoundAppError, UnsupportedFormatError
from devimage.core.models import ImageMetadata

logger = get_logger("engine.metadata")


def extract_metadata(image_path: str | Path) -> ImageMetadata:
    """Extract metadata from an image file without loading pixel data into memory.

    Args:
        image_path: Absolute or relative filesystem path to the image.

    Returns:
        ImageMetadata containing width, height, format, mode, file size, alpha flag, and DPI.

    Raises:
        FileNotFoundAppError: If the file does not exist on disk.
        UnsupportedFormatError: If Pillow cannot identify the file as an image.
    """
    path = Path(image_path).resolve()
    if not path.is_file():
        raise FileNotFoundAppError(str(path))

    file_size = os.path.getsize(path)

    try:
        with Image.open(path) as img:
            width, height = img.size
            img_format = img.format or path.suffix.lstrip(".").upper()
            mode = img.mode

            # Detect alpha/transparency
            has_alpha = mode in ("RGBA", "LA", "PA") or (
                "transparency" in img.info and mode in ("P", "L", "RGB")
            )

            # Extract DPI if available
            dpi: tuple[float, float] | None = None
            raw_dpi = img.info.get("dpi")
            if (
                raw_dpi
                and isinstance(raw_dpi, (tuple, list))
                and len(raw_dpi) >= 2
                and raw_dpi[0] > 0
            ):
                dpi = (float(raw_dpi[0]), float(raw_dpi[1]))

            return ImageMetadata(
                width=width,
                height=height,
                format=img_format,
                mode=mode,
                file_size_bytes=file_size,
                has_transparency=has_alpha,
                dpi=dpi,
            )
    except UnidentifiedImageError as err:
        logger.warning("Unidentified image file: %s (%s)", path, err)
        raise UnsupportedFormatError(str(path), format_name=path.suffix) from err
    except Exception as err:
        logger.error("Failed to extract metadata for %s: %s", path, err)
        raise UnsupportedFormatError(str(path), format_name=str(err)) from err
