"""Image processing sub-package."""

from devimage.engine.image.metadata import extract_metadata
from devimage.engine.image.processor import (
    calculate_aspect_dimensions,
    calculate_contain_dimensions,
    calculate_cover_dimensions,
    crop_image,
    open_image,
    resize_image,
    rotate_image,
    save_image,
)

__all__ = [
    "extract_metadata",
    "open_image",
    "save_image",
    "calculate_aspect_dimensions",
    "calculate_contain_dimensions",
    "calculate_cover_dimensions",
    "resize_image",
    "crop_image",
    "rotate_image",
]
