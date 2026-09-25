"""Core image processing operations using Pillow."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from devimage.app.logging import get_logger
from devimage.core.errors import (
    FileNotFoundAppError,
    ImageProcessingError,
    InvalidParameterError,
    UnsupportedFormatError,
)

logger = get_logger("engine.processor")

SUPPORTED_SAVE_FORMATS: dict[str, str] = {
    ".png": "PNG",
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".webp": "WEBP",
    ".bmp": "BMP",
    ".tiff": "TIFF",
    ".tif": "TIFF",
    ".gif": "GIF",
    ".ico": "ICO",
}


def open_image(image_path: str | Path) -> Image.Image:
    """Open an image file with automatic EXIF orientation transposition.

    Args:
        image_path: Path to the image file.

    Returns:
        Pillow Image instance loaded in memory.

    Raises:
        FileNotFoundAppError: If file is missing.
        UnsupportedFormatError: If file is not an image or is corrupted.
    """
    path = Path(image_path).resolve()
    if not path.is_file():
        raise FileNotFoundAppError(str(path))

    try:
        img = Image.open(path)
        img.load()  # Read pixel data into memory
        return ImageOps.exif_transpose(img)
    except UnidentifiedImageError as err:
        raise UnsupportedFormatError(str(path), format_name=path.suffix) from err
    except Exception as err:
        raise ImageProcessingError(
            description=f"Could not load image: {err}",
            details=str(path),
        ) from err


def save_image(
    image: Image.Image,
    output_path: str | Path,
    format_name: str | None = None,
    quality: int = 90,
    optimize: bool = True,
    strip_metadata: bool = False,
) -> str:
    """Save a Pillow Image to disk safely with format & quality normalization.

    Args:
        image: Pillow Image to save.
        output_path: Destination file path.
        format_name: Optional explicit format name (PNG, JPEG, WEBP, etc.).
        quality: Compression quality (1-100) for JPEG and WebP.
        optimize: Whether to run encoder optimizations.
        strip_metadata: If True, do not persist EXIF/ICC metadata.

    Returns:
        Resolved string path of the saved file.

    Raises:
        ImageProcessingError: If save fails.
    """
    dest = Path(output_path).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Determine format
    ext = dest.suffix.lower()
    target_format = format_name.upper() if format_name else SUPPORTED_SAVE_FORMATS.get(ext, "PNG")

    save_kwargs: dict[str, object] = {}

    # Handle transparency when saving to formats without alpha channel (e.g. JPEG)
    work_img = image
    if target_format == "JPEG":
        save_kwargs["quality"] = max(1, min(100, quality))
        save_kwargs["optimize"] = optimize
        if work_img.mode in ("RGBA", "LA", "P"):
            # Composite over clean white background
            background = Image.new("RGB", work_img.size, (255, 255, 255))
            if work_img.mode == "P":
                work_img = work_img.convert("RGBA")
            background.paste(work_img, mask=work_img.split()[-1])
            work_img = background
        elif work_img.mode != "RGB":
            work_img = work_img.convert("RGB")
    elif target_format == "WEBP":
        save_kwargs["quality"] = max(1, min(100, quality))
        save_kwargs["method"] = 6 if optimize else 4
    elif target_format == "PNG":
        save_kwargs["optimize"] = optimize

    # EXIF preservation
    if not strip_metadata and "exif" in image.info and target_format in ("JPEG", "WEBP"):
        save_kwargs["exif"] = image.info["exif"]

    try:
        work_img.save(dest, format=target_format, **save_kwargs)
        logger.info("Saved image to: %s (format: %s)", dest, target_format)
        return str(dest)
    except Exception as err:
        logger.error("Failed to save image to %s: %s", dest, err)
        raise ImageProcessingError(
            description=f"Failed to save image: {err}",
            details=str(dest),
        ) from err


def calculate_aspect_dimensions(
    orig_w: int,
    orig_h: int,
    target_w: int | None = None,
    target_h: int | None = None,
    keep_aspect: bool = True,
    dont_enlarge: bool = False,
) -> tuple[int, int]:
    """Calculate target dimensions preserving aspect ratio and upscale constraints.

    Args:
        orig_w: Original image width (> 0).
        orig_h: Original image height (> 0).
        target_w: Desired width (optional if target_h is given).
        target_h: Desired height (optional if target_w is given).
        keep_aspect: Whether to maintain original aspect ratio.
        dont_enlarge: If True, dimensions will not exceed original dimensions.

    Returns:
        Calculated (width, height) integers >= 1.
    """
    if orig_w <= 0 or orig_h <= 0:
        raise InvalidParameterError("dimensions", "Original dimensions must be positive integers.")

    aspect = orig_w / orig_h

    if target_w is None and target_h is None:
        target_w, target_h = orig_w, orig_h
    elif target_w is not None and target_h is None:
        if keep_aspect:
            target_h = max(1, round(target_w / aspect))
        else:
            target_h = orig_h
    elif target_h is not None and target_w is None:
        if keep_aspect:
            target_w = max(1, round(target_h * aspect))
        else:
            target_w = orig_w
    else:
        # Both provided
        assert target_w is not None and target_h is not None
        if keep_aspect:
            # Scale proportionally to fit within target bounding box
            scale = min(target_w / orig_w, target_h / orig_h)
            target_w = max(1, round(orig_w * scale))
            target_h = max(1, round(orig_h * scale))

    if dont_enlarge:
        if target_w > orig_w or target_h > orig_h:
            scale = min(orig_w / target_w, orig_h / target_h, 1.0)
            target_w = max(1, round(target_w * scale))
            target_h = max(1, round(target_h * scale))

    return max(1, target_w), max(1, target_h)


def calculate_contain_dimensions(
    orig_w: int, orig_h: int, bound_w: int, bound_h: int
) -> tuple[int, int]:
    """Calculate dimensions that fit entirely inside bounding box preserving aspect ratio."""
    scale = min(bound_w / orig_w, bound_h / orig_h)
    return max(1, round(orig_w * scale)), max(1, round(orig_h * scale))


def calculate_cover_dimensions(
    orig_w: int, orig_h: int, bound_w: int, bound_h: int
) -> tuple[int, int]:
    """Calculate dimensions that cover entire bounding box preserving aspect ratio."""
    scale = max(bound_w / orig_w, bound_h / orig_h)
    return max(1, round(orig_w * scale)), max(1, round(orig_h * scale))


def resize_image(
    image: Image.Image,
    target_w: int,
    target_h: int,
    mode: str = "contain",
    resample: Image.Resampling = Image.Resampling.LANCZOS,
) -> Image.Image:
    """Resize an image according to mode: 'contain', 'cover', or 'stretch'.

    Args:
        image: Source Pillow Image.
        target_w: Desired width.
        target_h: Desired height.
        mode: 'contain' (fit inside), 'cover' (fill and center crop), or 'stretch' (exact).
        resample: Pillow resampling filter (LANCZOS by default).

    Returns:
        Resized Pillow Image.
    """
    target_w = max(1, target_w)
    target_h = max(1, target_h)

    if mode == "stretch":
        return image.resize((target_w, target_h), resample=resample)

    if mode == "contain":
        w, h = calculate_contain_dimensions(image.width, image.height, target_w, target_h)
        return image.resize((w, h), resample=resample)

    if mode == "cover":
        w, h = calculate_cover_dimensions(image.width, image.height, target_w, target_h)
        resized = image.resize((w, h), resample=resample)
        # Center crop to target_w, target_h
        left = max(0, (w - target_w) // 2)
        top = max(0, (h - target_h) // 2)
        return resized.crop((left, top, left + target_w, top + target_h))

    # Default fallback to stretch
    return image.resize((target_w, target_h), resample=resample)


def crop_image(image: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    """Crop an image using pixel coordinates (left, top, right, bottom).

    Args:
        image: Source Pillow image.
        box: (left, top, right, bottom) pixel coordinates.

    Returns:
        Cropped Pillow Image.

    Raises:
        InvalidParameterError: If box boundaries are invalid or empty.
    """
    left, top, right, bottom = box

    if right <= left or bottom <= top:
        raise InvalidParameterError(
            "crop_box", "Crop dimensions must have right > left and bottom > top."
        )

    # Clamp coordinates to image boundaries
    left = max(0, min(image.width - 1, left))
    top = max(0, min(image.height - 1, top))
    right = max(left + 1, min(image.width, right))
    bottom = max(top + 1, min(image.height, bottom))

    return image.crop((left, top, right, bottom))


def rotate_image(image: Image.Image, angle: int, expand: bool = True) -> Image.Image:
    """Rotate image by specified degrees (e.g., 90, 180, 270).

    Args:
        image: Source Pillow Image.
        angle: Degrees clockwise (or counter-clockwise if negative).
        expand: Expand canvas so rotated image is not clipped.

    Returns:
        Rotated Pillow Image.
    """
    # Pillow rotate is counter-clockwise by default, so we invert or use transpose for 90/180/270
    normalized_angle = angle % 360
    if normalized_angle == 90:
        return image.transpose(Image.Transpose.ROTATE_270)
    elif normalized_angle == 180:
        return image.transpose(Image.Transpose.ROTATE_180)
    elif normalized_angle == 270:
        return image.transpose(Image.Transpose.ROTATE_90)
    elif normalized_angle == 0:
        return image.copy()
    else:
        # Arbitrary angle
        return image.rotate(-angle, expand=expand, resample=Image.Resampling.BICUBIC)
