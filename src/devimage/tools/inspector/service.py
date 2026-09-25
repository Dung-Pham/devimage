"""Image Inspector service for extracting technical metadata and EXIF."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any

from PIL import ExifTags, Image, UnidentifiedImageError

from devimage.app.logging import get_logger
from devimage.core.errors import FileNotFoundAppError, UnsupportedFormatError

logger = get_logger("tools.inspector.service")


def format_file_size(size_in_bytes: int) -> str:
    """Format file size into human-readable string (B, KB, MB, GB)."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    for unit in ["KB", "MB", "GB", "TB"]:
        size_in_bytes_float = size_in_bytes / 1024.0
        if size_in_bytes_float < 1024.0 or unit == "TB":
            return f"{size_in_bytes_float:.2f} {unit}"
        size_in_bytes = int(size_in_bytes_float)
    return f"{size_in_bytes} B"


def calculate_aspect_ratio_str(width: int, height: int) -> str:
    """Calculate common simplified aspect ratio or decimal representation."""
    if width <= 0 or height <= 0:
        return "Unknown"

    gcd = math.gcd(width, height)
    simplified_w = width // gcd
    simplified_h = height // gcd

    # Standard common ratios
    decimal = width / height
    common_ratios = [
        (16, 9),
        (9, 16),
        (4, 3),
        (3, 4),
        (1, 1),
        (21, 9),
        (3, 2),
        (2, 3),
        (5, 4),
        (4, 5),
    ]

    for cw, ch in common_ratios:
        if abs(decimal - (cw / ch)) < 0.015:
            return f"{cw}:{ch} ({decimal:.2f}:1)"

    if simplified_w < 50 and simplified_h < 50:
        return f"{simplified_w}:{simplified_h} ({decimal:.2f}:1)"

    return f"{decimal:.2f}:1"


class InspectorService:
    """Pure-Python non-destructive metadata inspector and analyzer."""

    def inspect(self, image_path: str | Path) -> dict[str, Any]:
        """Extract deep technical metadata, EXIF, and optimization advice.

        Args:
            image_path: Filesystem path to image.

        Returns:
            Dictionary with file info, geometry, color, exif, and optimization tips.
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

                # DPI
                dpi_val: tuple[float, float] | None = None
                raw_dpi = img.info.get("dpi")
                if (
                    raw_dpi
                    and isinstance(raw_dpi, (tuple, list))
                    and len(raw_dpi) >= 2
                    and raw_dpi[0] > 0
                ):
                    dpi_val = (round(float(raw_dpi[0]), 1), round(float(raw_dpi[1]), 1))

                # Color space / profile
                icc_profile_name = "sRGB (Standard)"
                if "icc_profile" in img.info:
                    icc_profile_name = (
                        f"Embedded ICC Profile ({len(img.info['icc_profile'])} bytes)"
                    )

                # EXIF metadata extraction
                exif_tags: dict[str, Any] = {}
                try:
                    raw_exif = img.getexif()
                    if raw_exif:
                        for tag_id, val in raw_exif.items():
                            tag_name = ExifTags.TAGS.get(tag_id, f"Tag_{tag_id}")
                            # Skip large binary thumbnails or undefined binary blobs
                            if isinstance(val, bytes):
                                if len(val) > 64:
                                    val_repr = f"<binary blob {len(val)} bytes>"
                                else:
                                    val_repr = val.hex()
                            else:
                                val_repr = str(val)
                            exif_tags[tag_name] = val_repr
                except Exception as e:
                    logger.debug("Failed parsing EXIF for %s: %s", path.name, e)

                # Generate optimization advice
                optimization_tips: list[str] = []
                if img_format in ("JPEG", "JPG") and file_size > 500_000:
                    optimization_tips.append(
                        f"Large JPEG ({format_file_size(file_size)}): Converting to WebP can save ~25-40% size."
                    )
                elif img_format == "PNG" and not has_alpha and file_size > 300_000:
                    optimization_tips.append(
                        "PNG without alpha channel: Converting to JPEG or WebP can dramatically reduce file size."
                    )
                elif img_format == "PNG" and has_alpha and file_size > 800_000:
                    optimization_tips.append(
                        "Large PNG with alpha: Converting to WebP preserves alpha with ~50-70% size reduction."
                    )
                elif img_format in ("BMP", "TIFF", "TIF"):
                    optimization_tips.append(
                        f"Uncompressed format ({img_format}): Converting to PNG or WebP is recommended for web/storage."
                    )

                if width > 3840 or height > 2160:
                    optimization_tips.append(
                        f"Ultra-high resolution ({width}x{height}): Downscaling may improve rendering performance."
                    )

                if not optimization_tips:
                    optimization_tips.append(
                        "Image is already reasonably optimized for its format."
                    )

                aspect_ratio_str = calculate_aspect_ratio_str(width, height)

                result: dict[str, Any] = {
                    "file_name": path.name,
                    "file_path": str(path),
                    "file_directory": str(path.parent),
                    "extension": path.suffix.lower(),
                    "file_size_bytes": file_size,
                    "file_size_formatted": format_file_size(file_size),
                    "format": img_format,
                    "width": width,
                    "height": height,
                    "dimensions": f"{width} × {height}",
                    "aspect_ratio": aspect_ratio_str,
                    "color_mode": mode,
                    "has_alpha": has_alpha,
                    "color_space": icc_profile_name,
                    "dpi": f"{dpi_val[0]} × {dpi_val[1]}"
                    if dpi_val
                    else "Not specified (72/96 typical)",
                    "dpi_values": dpi_val,
                    "has_exif": len(exif_tags) > 0,
                    "exif_count": len(exif_tags),
                    "exif_tags": exif_tags,
                    "optimization_tips": optimization_tips,
                }
                return result

        except UnidentifiedImageError as err:
            logger.warning("Unidentified image file: %s (%s)", path, err)
            raise UnsupportedFormatError(str(path), format_name=path.suffix) from err
        except Exception as err:
            logger.error("Failed to inspect %s: %s", path, err)
            raise UnsupportedFormatError(str(path), format_name=str(err)) from err

    def to_json(self, data: dict[str, Any], indent: int = 2) -> str:
        """Serialize inspected metadata to formatted JSON."""
        return json.dumps(data, indent=indent, ensure_ascii=False)

    def to_clipboard_text(self, data: dict[str, Any]) -> str:
        """Format inspected metadata into a clean text report for clipboard copying."""
        lines = [
            f"=== DevImage Inspector Report: {data.get('file_name', '')} ===",
            f"Path: {data.get('file_path', '')}",
            f"Format: {data.get('format', '')} ({data.get('extension', '')})",
            f"File Size: {data.get('file_size_formatted', '')} ({data.get('file_size_bytes', 0):,} bytes)",
            "",
            "--- Geometry ---",
            f"Dimensions: {data.get('dimensions', '')} px",
            f"Aspect Ratio: {data.get('aspect_ratio', '')}",
            f"DPI: {data.get('dpi', '')}",
            "",
            "--- Color & Channels ---",
            f"Color Mode: {data.get('color_mode', '')}",
            f"Alpha / Transparency: {'Yes' if data.get('has_alpha') else 'No'}",
            f"Color Space: {data.get('color_space', '')}",
        ]

        exif = data.get("exif_tags", {})
        if exif:
            lines.append("")
            lines.append(f"--- EXIF Metadata ({len(exif)} tags) ---")
            for k, v in sorted(exif.items()):
                lines.append(f"{k}: {v}")

        tips = data.get("optimization_tips", [])
        if tips:
            lines.append("")
            lines.append("--- Optimization Analysis ---")
            for tip in tips:
                lines.append(f"• {tip}")

        return "\n".join(lines)
