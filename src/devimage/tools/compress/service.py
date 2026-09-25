"""Pure-Python compression service implementing standalone image compression."""

from __future__ import annotations

import io
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image

from devimage.app.logging import get_logger
from devimage.core.errors import (
    FileNotFoundAppError,
    InvalidParameterError,
)
from devimage.engine.image.processor import open_image, save_image

logger = get_logger("tools.compress.service")


@dataclass
class CompressOptions:
    """Configuration options for image compression."""

    quality: int = 80  # 1-100
    target_format: str = "original"  # "original", "webp", "jpeg", "png"
    strip_metadata: bool = True
    optimize: bool = True
    png_quantize: bool = False


@dataclass
class CompressResult:
    """Summary of completed compression operation."""

    input_path: str
    output_path: str
    original_size_bytes: int
    compressed_size_bytes: int
    reduction_percent: float
    format_name: str
    success: bool = True
    error_message: str = ""


class CompressService:
    """Standalone service executing image compression and size estimation."""

    @staticmethod
    def resolve_format(input_path: str | Path, target_format: str) -> str:
        """Resolve final format name ('PNG', 'JPEG', 'WEBP')."""
        if target_format == "original" or not target_format:
            suffix = Path(input_path).suffix.lower()
            if suffix in (".jpg", ".jpeg"):
                return "JPEG"
            if suffix == ".webp":
                return "WEBP"
            if suffix == ".png":
                return "PNG"
            return suffix.lstrip(".").upper() or "PNG"

        norm = target_format.lower()
        if norm in ("jpg", "jpeg"):
            return "JPEG"
        if norm == "webp":
            return "WEBP"
        if norm == "png":
            return "PNG"
        return target_format.upper()

    @classmethod
    def estimate_compression(
        cls,
        input_path: str | Path,
        options: CompressOptions,
    ) -> tuple[int, float]:
        """Estimate output file size and reduction percentage via in-memory encoding.

        Args:
            input_path: Path to source image.
            options: CompressOptions settings.

        Returns:
            Tuple of (estimated_size_bytes, reduction_percentage).
        """
        src = Path(input_path).resolve()
        if not src.is_file():
            raise FileNotFoundAppError(str(src))

        orig_size = os.path.getsize(src)
        format_name = cls.resolve_format(src, options.target_format)

        img = open_image(src)

        # Handle quantization if requested for PNG
        work_img = img
        if format_name == "PNG" and options.png_quantize:
            if work_img.mode in ("RGBA", "RGB"):
                work_img = work_img.quantize(colors=256)

        # Handle alpha channel composite for JPEG
        if format_name == "JPEG":
            if work_img.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", work_img.size, (255, 255, 255))
                if work_img.mode == "P":
                    work_img = work_img.convert("RGBA")
                bg.paste(work_img, mask=work_img.split()[-1])
                work_img = bg
            elif work_img.mode != "RGB":
                work_img = work_img.convert("RGB")

        buffer = io.BytesIO()
        save_kwargs: dict[str, object] = {}

        if format_name in ("JPEG", "WEBP"):
            save_kwargs["quality"] = max(1, min(100, options.quality))
            save_kwargs["optimize"] = options.optimize
            if format_name == "WEBP":
                save_kwargs["method"] = 6 if options.optimize else 4
        elif format_name == "PNG":
            save_kwargs["optimize"] = options.optimize

        if not options.strip_metadata and "exif" in img.info and format_name in ("JPEG", "WEBP"):
            save_kwargs["exif"] = img.info["exif"]

        work_img.save(buffer, format=format_name, **save_kwargs)
        estimated_size = buffer.tell()

        reduction = 0.0
        if orig_size > 0:
            reduction = max(0.0, ((orig_size - estimated_size) / orig_size) * 100.0)

        return estimated_size, round(reduction, 1)

    @classmethod
    def get_default_output_path(
        cls,
        input_path: str | Path,
        output_dir: str | Path | None = None,
        target_format: str = "original",
        suffix: str = "_compressed",
    ) -> Path:
        """Generate a safe, non-destructive destination path for compressed image."""
        src = Path(input_path).resolve()
        parent_dir = Path(output_dir).resolve() if output_dir else src.parent

        resolved_fmt = cls.resolve_format(src, target_format)
        ext_map = {"JPEG": ".jpg", "WEBP": ".webp", "PNG": ".png"}
        ext = ext_map.get(resolved_fmt, src.suffix)

        candidate = parent_dir / f"{src.stem}{suffix}{ext}"
        if not candidate.exists():
            return candidate

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
        options: CompressOptions | None = None,
        progress_callback: Callable[[float, str], None] | None = None,
    ) -> CompressResult:
        """Execute single-image compression synchronously.

        Args:
            input_path: Source image file path.
            output_path: Destination path (auto-generated if None).
            options: Compression configuration options.
            progress_callback: Optional progress reporter (pct, message).

        Returns:
            CompressResult detailing compression statistics.
        """
        src = Path(input_path).resolve()
        if not src.is_file():
            raise FileNotFoundAppError(str(src))

        orig_size = os.path.getsize(src)

        if options is None:
            options = CompressOptions()

        if options.quality < 1 or options.quality > 100:
            raise InvalidParameterError(
                "quality", f"Quality must be between 1 and 100, got {options.quality}"
            )

        if progress_callback:
            progress_callback(10.0, "Loading source image...")

        img = open_image(src)
        format_name = self.resolve_format(src, options.target_format)

        if progress_callback:
            progress_callback(40.0, f"Optimizing image for {format_name} format...")

        work_img = img
        if format_name == "PNG" and options.png_quantize:
            if work_img.mode in ("RGBA", "RGB"):
                work_img = work_img.quantize(colors=256)

        dest = Path(
            output_path or self.get_default_output_path(src, target_format=options.target_format)
        ).resolve()

        if progress_callback:
            progress_callback(70.0, "Encoding and saving compressed image...")

        save_image(
            image=work_img,
            output_path=dest,
            format_name=format_name,
            quality=options.quality,
            optimize=options.optimize,
            strip_metadata=options.strip_metadata,
        )

        compressed_size = os.path.getsize(dest)
        reduction = 0.0
        if orig_size > 0:
            reduction = max(0.0, ((orig_size - compressed_size) / orig_size) * 100.0)

        if progress_callback:
            progress_callback(100.0, "Compression completed successfully.")

        logger.info(
            "Compressed '%s' (%d bytes) -> '%s' (%d bytes, -%.1f%%)",
            src.name,
            orig_size,
            dest.name,
            compressed_size,
            reduction,
        )

        return CompressResult(
            input_path=str(src),
            output_path=str(dest),
            original_size_bytes=orig_size,
            compressed_size_bytes=compressed_size,
            reduction_percent=round(reduction, 1),
            format_name=format_name,
            success=True,
        )

    def execute_batch(
        self,
        input_paths: list[str | Path],
        output_dir: str | Path | None = None,
        options: CompressOptions | None = None,
        progress_callback: Callable[[float, str], None] | None = None,
        cancel_check: Callable[[], bool] | None = None,
    ) -> list[CompressResult]:
        """Execute compression on a batch of files sequentially with cancellation checks."""
        results: list[CompressResult] = []
        total = len(input_paths)
        if total == 0:
            return results

        for idx, item in enumerate(input_paths):
            if cancel_check and cancel_check():
                logger.info("Batch compress cancelled at item %d/%d", idx, total)
                break

            pct = (idx / total) * 100.0
            if progress_callback:
                progress_callback(pct, f"Compressing {Path(item).name} ({idx + 1}/{total})...")

            try:
                dest = self.get_default_output_path(
                    input_path=item,
                    output_dir=output_dir,
                    target_format=options.target_format if options else "original",
                )
                res = self.execute(
                    input_path=item,
                    output_path=dest,
                    options=options,
                )
                results.append(res)
            except Exception as err:
                logger.error("Error compressing batch file %s: %s", item, err)
                results.append(
                    CompressResult(
                        input_path=str(item),
                        output_path="",
                        original_size_bytes=0,
                        compressed_size_bytes=0,
                        reduction_percent=0.0,
                        format_name="",
                        success=False,
                        error_message=str(err),
                    )
                )

        if progress_callback:
            progress_callback(100.0, f"Batch compression complete ({len(results)}/{total} items).")

        return results
