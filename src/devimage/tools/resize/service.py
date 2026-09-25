"""Pure-Python resize service implementing standalone resize operations."""

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
from devimage.engine.image.processor import open_image, resize_image, save_image

logger = get_logger("tools.resize.service")


@dataclass
class ResizeOptions:
    """Configuration options for image resizing."""

    target_width: int
    target_height: int
    mode: str = "contain"  # "contain", "cover", "stretch"
    keep_aspect: bool = True
    dont_enlarge: bool = False
    output_format: str | None = None
    quality: int = 90


@dataclass
class ResizeResult:
    """Summary of completed resize operation."""

    input_path: str
    output_path: str
    original_width: int
    original_height: int
    target_width: int
    target_height: int
    file_size_bytes: int
    success: bool = True
    error_message: str = ""


class ResizeService:
    """Standalone service executing image resize logic offline."""

    PRESETS: list[int] = [1920, 1600, 1200, 1024, 768, 480]

    @staticmethod
    def calculate_dimensions(
        orig_w: int,
        orig_h: int,
        target_w: int,
        target_h: int,
        keep_aspect: bool = True,
        dont_enlarge: bool = False,
        mode: str = "contain",
    ) -> tuple[int, int]:
        """Calculate final pixel dimensions based on aspect ratio, constraints, and mode.

        Args:
            orig_w: Original image width.
            orig_h: Original image height.
            target_w: Requested target width.
            target_h: Requested target height.
            keep_aspect: Whether to preserve aspect ratio.
            dont_enlarge: Prevent upscale if requested size is larger than original.
            mode: Resize mode ('contain', 'cover', 'stretch').

        Returns:
            Calculated (width, height) tuple >= 1.
        """
        if orig_w <= 0 or orig_h <= 0:
            raise InvalidParameterError(
                "dimensions", "Original dimensions must be positive integers."
            )
        if target_w <= 0 or target_h <= 0:
            raise InvalidParameterError(
                "dimensions", "Target dimensions must be positive integers."
            )

        if mode == "stretch" or not keep_aspect:
            w, h = target_w, target_h
            if dont_enlarge:
                w = min(w, orig_w)
                h = min(h, orig_h)
            return max(1, w), max(1, h)

        if mode == "contain":
            scale = min(target_w / orig_w, target_h / orig_h)
            if dont_enlarge:
                scale = min(scale, 1.0)
            return max(1, round(orig_w * scale)), max(1, round(orig_h * scale))

        if mode == "cover":
            if dont_enlarge and (target_w > orig_w or target_h > orig_h):
                scale = min(orig_w / target_w, orig_h / target_h, 1.0)
                w = max(1, round(target_w * scale))
                h = max(1, round(target_h * scale))
                return w, h
            return max(1, target_w), max(1, target_h)

        # Fallback default
        return max(1, target_w), max(1, target_h)

    @classmethod
    def calculate_preset(
        cls,
        orig_w: int,
        orig_h: int,
        preset_max_dim: int,
        keep_aspect: bool = True,
    ) -> tuple[int, int]:
        """Calculate dimensions fitting a standard resolution preset (e.g. 1920, 1600).

        Args:
            orig_w: Original width.
            orig_h: Original height.
            preset_max_dim: Maximum dimension for preset bounding box.
            keep_aspect: Whether to maintain aspect ratio.

        Returns:
            Calculated (width, height) tuple.
        """
        if preset_max_dim <= 0:
            raise InvalidParameterError(
                "preset_max_dim", f"Preset dimension must be > 0, got {preset_max_dim}"
            )

        if not keep_aspect:
            return preset_max_dim, preset_max_dim

        if orig_w >= orig_h:
            target_w = preset_max_dim
            target_h = max(1, round(preset_max_dim * (orig_h / orig_w)))
        else:
            target_h = preset_max_dim
            target_w = max(1, round(preset_max_dim * (orig_w / orig_h)))

        return target_w, target_h

    @staticmethod
    def get_default_output_path(
        input_path: str | Path,
        output_dir: str | Path | None = None,
        suffix: str = "_resized",
        target_format: str | None = None,
    ) -> Path:
        """Generate a safe, non-destructive destination path for resized output."""
        src = Path(input_path).resolve()
        parent_dir = Path(output_dir).resolve() if output_dir else src.parent

        ext = f".{target_format.lower()}" if target_format else src.suffix
        if not ext.startswith("."):
            ext = f".{ext}"

        candidate = parent_dir / f"{src.stem}{suffix}{ext}"
        if not candidate.exists():
            return candidate

        # Disambiguate collision if file already exists
        counter = 1
        while True:
            candidate = parent_dir / f"{src.stem}{suffix}_{counter}{ext}"
            if not candidate.exists():
                return candidate
            counter += 1

    def execute(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        options: ResizeOptions | None = None,
        progress_callback: Callable[[float, str], None] | None = None,
    ) -> ResizeResult:
        """Execute single-image resize operation synchronously.

        Args:
            input_path: Source image file path.
            output_path: Destination file path (auto-generated if None).
            options: ResizeOptions configuration.
            progress_callback: Optional callback for progress reporting (0.0 - 100.0, message).

        Returns:
            ResizeResult detailing processed file information.
        """
        src = Path(input_path).resolve()
        if not src.is_file():
            raise FileNotFoundAppError(str(src))

        if progress_callback:
            progress_callback(10.0, "Loading source image...")

        img = open_image(src)
        orig_w, orig_h = img.width, img.height

        if options is None:
            options = ResizeOptions(target_width=orig_w, target_height=orig_h)

        if progress_callback:
            progress_callback(30.0, "Calculating target dimensions...")

        final_w, final_h = self.calculate_dimensions(
            orig_w=orig_w,
            orig_h=orig_h,
            target_w=options.target_width,
            target_h=options.target_height,
            keep_aspect=options.keep_aspect,
            dont_enlarge=options.dont_enlarge,
            mode=options.mode,
        )

        if progress_callback:
            progress_callback(50.0, f"Resizing image to {final_w}x{final_h}...")

        resized_img = resize_image(
            image=img,
            target_w=final_w,
            target_h=final_h,
            mode=options.mode,
        )

        dest = Path(
            output_path or self.get_default_output_path(src, target_format=options.output_format)
        ).resolve()

        if progress_callback:
            progress_callback(80.0, "Saving resized image...")

        save_image(
            image=resized_img,
            output_path=dest,
            format_name=options.output_format,
            quality=options.quality,
        )

        file_size = os.path.getsize(dest)

        if progress_callback:
            progress_callback(100.0, "Resize completed successfully.")

        logger.info(
            "Resized '%s' (%dx%d) -> '%s' (%dx%d, %d bytes)",
            src.name,
            orig_w,
            orig_h,
            dest.name,
            resized_img.width,
            resized_img.height,
            file_size,
        )

        return ResizeResult(
            input_path=str(src),
            output_path=str(dest),
            original_width=orig_w,
            original_height=orig_h,
            target_width=resized_img.width,
            target_height=resized_img.height,
            file_size_bytes=file_size,
            success=True,
        )

    def execute_batch(
        self,
        input_paths: list[str | Path],
        output_dir: str | Path | None = None,
        options: ResizeOptions | None = None,
        progress_callback: Callable[[float, str], None] | None = None,
        cancel_check: Callable[[], bool] | None = None,
    ) -> list[ResizeResult]:
        """Execute resize on a batch of files sequentially with cancellation checks.

        Args:
            input_paths: List of file paths to process.
            output_dir: Directory where outputs are written (defaults to each file's parent).
            options: ResizeOptions applied to each image.
            progress_callback: Progress callback reporting aggregate percentage.
            cancel_check: Callable returning True if cancellation was requested.

        Returns:
            List of ResizeResult for each processed file.
        """
        results: list[ResizeResult] = []
        total = len(input_paths)
        if total == 0:
            return results

        for idx, item in enumerate(input_paths):
            if cancel_check and cancel_check():
                logger.info("Batch resize cancelled at item %d/%d", idx, total)
                break

            pct = (idx / total) * 100.0
            if progress_callback:
                progress_callback(pct, f"Processing {Path(item).name} ({idx + 1}/{total})...")

            try:
                dest = self.get_default_output_path(
                    input_path=item,
                    output_dir=output_dir,
                    target_format=options.output_format if options else None,
                )
                res = self.execute(
                    input_path=item,
                    output_path=dest,
                    options=options,
                )
                results.append(res)
            except Exception as err:
                logger.error("Error resizing batch file %s: %s", item, err)
                results.append(
                    ResizeResult(
                        input_path=str(item),
                        output_path="",
                        original_width=0,
                        original_height=0,
                        target_width=0,
                        target_height=0,
                        file_size_bytes=0,
                        success=False,
                        error_message=str(err),
                    )
                )

        if progress_callback:
            progress_callback(100.0, f"Batch completed ({len(results)}/{total} items).")

        return results
