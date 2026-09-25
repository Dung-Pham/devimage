"""Pure-Python format conversion service implementing standalone image conversion."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image

from devimage.app.logging import get_logger
from devimage.core.errors import (
    FileNotFoundAppError,
    InvalidParameterError,
    UnsupportedFormatError,
)
from devimage.engine.image.processor import open_image, save_image

logger = get_logger("tools.convert.service")

SUPPORTED_TARGET_FORMATS: dict[str, tuple[str, str]] = {
    "png": ("PNG", ".png"),
    "jpeg": ("JPEG", ".jpg"),
    "jpg": ("JPEG", ".jpg"),
    "webp": ("WEBP", ".webp"),
}


@dataclass
class ConvertOptions:
    """Configuration options for format conversion."""

    target_format: str = "webp"  # "png", "jpeg", "webp"
    quality: int = 90  # For JPEG and WebP
    strip_metadata: bool = False
    optimize: bool = True
    background_color: tuple[int, int, int] = (255, 255, 255)


@dataclass
class ConvertResult:
    """Summary of completed format conversion."""

    input_path: str
    output_path: str
    original_format: str
    target_format: str
    file_size_bytes: int
    success: bool = True
    error_message: str = ""


class ConvertService:
    """Standalone format conversion service."""

    @staticmethod
    def normalize_target_format(format_name: str) -> tuple[str, str]:
        """Normalize format name to (PIL_FORMAT, extension)."""
        key = format_name.lower().lstrip(".")
        if key not in SUPPORTED_TARGET_FORMATS:
            raise UnsupportedFormatError(
                file_path="",
                format_name=f"Unsupported target format: '{format_name}'. Supported: PNG, JPEG, WEBP.",
            )
        return SUPPORTED_TARGET_FORMATS[key]

    @classmethod
    def get_default_output_path(
        cls,
        input_path: str | Path,
        target_format: str,
        output_dir: str | Path | None = None,
        custom_stem: str | None = None,
    ) -> Path:
        """Generate safe, non-destructive destination path for converted file."""
        src = Path(input_path).resolve()
        parent_dir = Path(output_dir).resolve() if output_dir else src.parent
        _, ext = cls.normalize_target_format(target_format)

        stem = custom_stem or src.stem
        # If output has same stem and extension in same directory, append suffix
        suffix = (
            "_converted" if (ext.lower() == src.suffix.lower() and parent_dir == src.parent) else ""
        )

        candidate = parent_dir / f"{stem}{suffix}{ext}"
        if not candidate.exists():
            return candidate

        counter = 1
        while True:
            candidate = parent_dir / f"{stem}{suffix}_{counter}{ext}"
            if not candidate.exists():
                return candidate
            counter += 1

    def execute(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        options: ConvertOptions | None = None,
        progress_callback: Callable[[float, str], None] | None = None,
    ) -> ConvertResult:
        """Execute single-image format conversion synchronously.

        Args:
            input_path: Source image file path.
            output_path: Optional explicit destination path.
            options: Conversion options.
            progress_callback: Optional progress reporter (pct, message).

        Returns:
            ConvertResult detailing converted image.
        """
        src = Path(input_path).resolve()
        if not src.is_file():
            raise FileNotFoundAppError(str(src))

        if options is None:
            options = ConvertOptions()

        if options.quality < 1 or options.quality > 100:
            raise InvalidParameterError(
                "quality", f"Quality must be between 1 and 100, got {options.quality}"
            )

        pil_format, _ = self.normalize_target_format(options.target_format)

        if progress_callback:
            progress_callback(10.0, f"Opening {src.name}...")

        img = open_image(src)
        orig_format = img.format or src.suffix.lstrip(".").upper()

        if progress_callback:
            progress_callback(40.0, f"Transforming color spaces for {pil_format}...")

        work_img = img

        # Alpha flattening when converting transparent images to formats without alpha (e.g. JPEG)
        if pil_format == "JPEG":
            if work_img.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", work_img.size, options.background_color)
                if work_img.mode == "P":
                    work_img = work_img.convert("RGBA")
                alpha_mask = work_img.split()[-1]
                bg.paste(work_img, mask=alpha_mask)
                work_img = bg
            elif work_img.mode != "RGB":
                work_img = work_img.convert("RGB")

        dest = Path(
            output_path or self.get_default_output_path(src, target_format=options.target_format)
        ).resolve()

        if progress_callback:
            progress_callback(70.0, f"Writing {dest.name}...")

        save_image(
            image=work_img,
            output_path=dest,
            format_name=pil_format,
            quality=options.quality,
            optimize=options.optimize,
            strip_metadata=options.strip_metadata,
        )

        file_size = os.path.getsize(dest)

        if progress_callback:
            progress_callback(100.0, "Conversion completed.")

        logger.info(
            "Converted '%s' (%s) -> '%s' (%s, %d bytes)",
            src.name,
            orig_format,
            dest.name,
            pil_format,
            file_size,
        )

        return ConvertResult(
            input_path=str(src),
            output_path=str(dest),
            original_format=orig_format,
            target_format=pil_format,
            file_size_bytes=file_size,
            success=True,
        )

    def execute_batch(
        self,
        input_paths: list[str | Path],
        output_dir: str | Path | None = None,
        options: ConvertOptions | None = None,
        progress_callback: Callable[[float, str], None] | None = None,
        cancel_check: Callable[[], bool] | None = None,
    ) -> list[ConvertResult]:
        """Convert a batch of files sequentially with cancellation checks."""
        results: list[ConvertResult] = []
        total = len(input_paths)
        if total == 0:
            return results

        for idx, item in enumerate(input_paths):
            if cancel_check and cancel_check():
                logger.info("Batch conversion cancelled at item %d/%d", idx, total)
                break

            pct = (idx / total) * 100.0
            if progress_callback:
                progress_callback(pct, f"Converting {Path(item).name} ({idx + 1}/{total})...")

            try:
                dest = self.get_default_output_path(
                    input_path=item,
                    target_format=options.target_format if options else "webp",
                    output_dir=output_dir,
                )
                res = self.execute(
                    input_path=item,
                    output_path=dest,
                    options=options,
                )
                results.append(res)
            except Exception as err:
                logger.error("Error converting file %s: %s", item, err)
                results.append(
                    ConvertResult(
                        input_path=str(item),
                        output_path="",
                        original_format="",
                        target_format="",
                        file_size_bytes=0,
                        success=False,
                        error_message=str(err),
                    )
                )

        if progress_callback:
            progress_callback(100.0, f"Batch conversion complete ({len(results)}/{total} items).")

        return results
