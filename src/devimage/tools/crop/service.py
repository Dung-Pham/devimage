"""Pure-Python crop service implementing standalone image cropping and rotation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from devimage.app.logging import get_logger
from devimage.core.errors import (
    FileNotFoundAppError,
    InvalidParameterError,
)
from devimage.engine.image.processor import (
    crop_image,
    open_image,
    rotate_image,
    save_image,
)

logger = get_logger("tools.crop.service")


@dataclass
class CropOptions:
    """Configuration options for image cropping and orientation."""

    crop_box: tuple[int, int, int, int] | None = None  # (left, top, right, bottom)
    rotation: int = 0  # 0, 90, 180, 270
    quality: int = 90


@dataclass
class CropResult:
    """Summary of completed crop operation."""

    input_path: str
    output_path: str
    original_width: int
    original_height: int
    cropped_width: int
    cropped_height: int
    rotation: int
    file_size_bytes: int
    success: bool = True
    error_message: str = ""


class CropService:
    """Standalone image cropping and orientation service."""

    @staticmethod
    def clamp_box(
        box: tuple[int, int, int, int], img_w: int, img_h: int
    ) -> tuple[int, int, int, int]:
        """Ensure crop coordinates are within image boundaries and valid."""
        left, top, right, bottom = box

        if right <= left or bottom <= top:
            raise InvalidParameterError(
                "crop_box",
                f"Invalid crop boundaries ({left}, {top}, {right}, {bottom}) for image {img_w}x{img_h}",
            )

        left = max(0, min(img_w - 1, left))
        top = max(0, min(img_h - 1, top))
        right = max(left + 1, min(img_w, right))
        bottom = max(top + 1, min(img_h, bottom))

        return left, top, right, bottom

    @classmethod
    def calculate_center_crop(
        cls, orig_w: int, orig_h: int, aspect_w: int, aspect_h: int
    ) -> tuple[int, int, int, int]:
        """Calculate a centered crop box matching the requested aspect ratio.

        Args:
            orig_w: Image width.
            orig_h: Image height.
            aspect_w: Aspect width ratio (e.g. 16).
            aspect_h: Aspect height ratio (e.g. 9).

        Returns:
            (left, top, right, bottom) coordinates.
        """
        if orig_w <= 0 or orig_h <= 0 or aspect_w <= 0 or aspect_h <= 0:
            raise InvalidParameterError(
                "aspect", "Dimensions and aspect ratios must be positive integers."
            )

        target_ratio = aspect_w / aspect_h
        current_ratio = orig_w / orig_h

        if current_ratio > target_ratio:
            # Image is wider than target ratio -> fit height, crop width
            crop_h = orig_h
            crop_w = max(1, round(orig_h * target_ratio))
            left = (orig_w - crop_w) // 2
            top = 0
        else:
            # Image is taller than target ratio -> fit width, crop height
            crop_w = orig_w
            crop_h = max(1, round(orig_w / target_ratio))
            left = 0
            top = (orig_h - crop_h) // 2

        right = left + crop_w
        bottom = top + crop_h

        return cls.clamp_box((left, top, right, bottom), orig_w, orig_h)

    @staticmethod
    def get_default_output_path(
        input_path: str | Path,
        output_dir: str | Path | None = None,
        suffix: str = "_cropped",
    ) -> Path:
        """Generate safe, non-destructive destination path for cropped output."""
        src = Path(input_path).resolve()
        parent_dir = Path(output_dir).resolve() if output_dir else src.parent

        candidate = parent_dir / f"{src.stem}{suffix}{src.suffix}"
        if not candidate.exists():
            return candidate

        counter = 1
        while True:
            candidate = parent_dir / f"{src.stem}{suffix}_{counter}{src.suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def execute(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        options: CropOptions | None = None,
        progress_callback: Callable[[float, str], None] | None = None,
    ) -> CropResult:
        """Execute image rotation and cropping synchronously.

        Args:
            input_path: Source image file path.
            output_path: Destination path (auto-generated if None).
            options: CropOptions configuration.
            progress_callback: Optional progress reporter (pct, message).

        Returns:
            CropResult detailing cropped image dimensions and file size.
        """
        src = Path(input_path).resolve()
        if not src.is_file():
            raise FileNotFoundAppError(str(src))

        if options is None:
            options = CropOptions()

        if progress_callback:
            progress_callback(10.0, "Loading source image...")

        img = open_image(src)
        orig_w, orig_h = img.width, img.height

        # 1. Apply rotation if specified
        work_img = img
        rot = options.rotation % 360
        if rot != 0:
            if progress_callback:
                progress_callback(30.0, f"Rotating image by {rot}°...")
            work_img = rotate_image(work_img, rot, expand=True)

        cur_w, cur_h = work_img.width, work_img.height

        # 2. Apply crop if crop_box specified
        if options.crop_box:
            if progress_callback:
                progress_callback(60.0, "Applying crop boundaries...")
            box = self.clamp_box(options.crop_box, cur_w, cur_h)
            work_img = crop_image(work_img, box)

        dest = Path(output_path or self.get_default_output_path(src)).resolve()

        if progress_callback:
            progress_callback(80.0, "Saving cropped image...")

        save_image(
            image=work_img,
            output_path=dest,
            quality=options.quality,
        )

        file_size = os.path.getsize(dest)

        if progress_callback:
            progress_callback(100.0, "Cropping completed successfully.")

        logger.info(
            "Cropped '%s' (%dx%d) -> '%s' (%dx%d, %d bytes)",
            src.name,
            orig_w,
            orig_h,
            dest.name,
            work_img.width,
            work_img.height,
            file_size,
        )

        return CropResult(
            input_path=str(src),
            output_path=str(dest),
            original_width=orig_w,
            original_height=orig_h,
            cropped_width=work_img.width,
            cropped_height=work_img.height,
            rotation=rot,
            file_size_bytes=file_size,
            success=True,
        )
