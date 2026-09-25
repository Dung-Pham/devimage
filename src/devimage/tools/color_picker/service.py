"""Color Picker service for pixel sampling, color conversions, and palette extraction."""

from __future__ import annotations

import colorsys
from pathlib import Path
from typing import Any

from PIL import Image

from devimage.app.logging import get_logger
from devimage.core.errors import FileNotFoundAppError, UnsupportedFormatError

logger = get_logger("tools.color_picker.service")


def rgb_to_hex(r: int, g: int, b: int, a: int = 255) -> str:
    """Format RGB(A) values to uppercase hexadecimal string."""
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    a = max(0, min(255, int(a)))
    if a < 255:
        return f"#{r:02X}{g:02X}{b:02X}{a:02X}"
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_rgb(hex_code: str) -> tuple[int, int, int, int]:
    """Parse hex string to (r, g, b, a) tuple."""
    clean = hex_code.strip().lstrip("#")
    if len(clean) == 3:
        # #RGB -> #RRGGBB
        clean = "".join(c * 2 for c in clean) + "FF"
    elif len(clean) == 4:
        # #RGBA -> #RRGGBBAA
        clean = "".join(c * 2 for c in clean)
    elif len(clean) == 6:
        clean += "FF"
    elif len(clean) != 8:
        raise ValueError(f"Invalid hex color code: {hex_code}")

    r = int(clean[0:2], 16)
    g = int(clean[2:4], 16)
    b = int(clean[4:6], 16)
    a = int(clean[6:8], 16)
    return r, g, b, a


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Convert RGB (0-255) to HSL (0-360, 0-100%, 0-100%)."""
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    h_norm, l_norm, s_norm = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
    h = round(h_norm * 360) % 360
    s = round(s_norm * 100)
    l_val = round(l_norm * 100)
    return h, s, l_val


def rgb_to_hsv(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Convert RGB (0-255) to HSV (0-360, 0-100%, 0-100%)."""
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    h_norm, s_norm, v_norm = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
    h = round(h_norm * 360) % 360
    s = round(s_norm * 100)
    v = round(v_norm * 100)
    return h, s, v


def get_contrast_color(r: int, g: int, b: int) -> str:
    """Calculate luminance and return white or black for optimal contrast."""
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    return "#000000" if luminance > 0.55 else "#ffffff"


def build_color_bundle(
    r: int, g: int, b: int, a: int = 255, x: int = 0, y: int = 0
) -> dict[str, Any]:
    """Package color representations into a unified dictionary."""
    hex_str = rgb_to_hex(r, g, b)
    hex_alpha_str = rgb_to_hex(r, g, b, a)
    h, s, l_val = rgb_to_hsl(r, g, b)
    h_v, s_v, v = rgb_to_hsv(r, g, b)

    if a < 255:
        a_frac = round(a / 255.0, 2)
        rgb_str = f"rgba({r}, {g}, {b}, {a_frac})"
        hsl_str = f"hsla({h}, {s}%, {l_val}%, {a_frac})"
    else:
        rgb_str = f"rgb({r}, {g}, {b})"
        hsl_str = f"hsl({h}, {s}%, {l_val}%)"

    contrast = get_contrast_color(r, g, b)

    return {
        "x": x,
        "y": y,
        "r": r,
        "g": g,
        "b": b,
        "a": a,
        "hex": hex_str,
        "hex_alpha": hex_alpha_str,
        "rgb_str": rgb_str,
        "hsl_str": hsl_str,
        "h": h,
        "s": s,
        "l": l_val,
        "hsv_h": h_v,
        "hsv_s": s_v,
        "hsv_v": v,
        "css_var": f"--color-sampled: {hex_str};",
        "contrast_text": contrast,
    }


class ColorService:
    """Pure-Python service for color sampling and palette analysis."""

    def __init__(self) -> None:
        self._cached_path: str = ""
        self._cached_image: Image.Image | None = None

    def _get_image(self, image_path: str) -> Image.Image:
        """Load and cache PIL Image for fast repeated pixel sampling."""
        if not image_path:
            raise FileNotFoundAppError(image_path)

        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundAppError(image_path)

        if self._cached_path == image_path and self._cached_image is not None:
            return self._cached_image

        try:
            img = Image.open(path)
            # Ensure RGBA or RGB
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert(
                    "RGBA" if "A" in img.mode or img.info.get("transparency") is not None else "RGB"
                )
            self._cached_path = image_path
            self._cached_image = img
            return img
        except Exception as err:
            logger.error("Failed to open image for color picker %s: %s", image_path, err)
            raise UnsupportedFormatError(path.suffix, f"Cannot open image: {err}") from err

    def sample_pixel(self, image_path: str, x: int, y: int) -> dict[str, Any]:
        """Sample exact pixel RGBA at coordinate (x, y) and return formatted color representations."""
        img = self._get_image(image_path)
        w, h = img.size

        # Clamp coordinate bounds
        clamped_x = max(0, min(w - 1, int(x)))
        clamped_y = max(0, min(h - 1, int(y)))

        pixel = img.getpixel((clamped_x, clamped_y))
        if isinstance(pixel, tuple):
            if len(pixel) >= 4:
                r, g, b, a = pixel[0], pixel[1], pixel[2], pixel[3]
            elif len(pixel) == 3:
                r, g, b, a = pixel[0], pixel[1], pixel[2], 255
            else:
                r = g = b = pixel[0]
                a = 255
        else:
            r = g = b = int(pixel)
            a = 255

        return build_color_bundle(r, g, b, a, x=clamped_x, y=clamped_y)

    def extract_palette(self, image_path: str, max_colors: int = 8) -> list[dict[str, Any]]:
        """Extract dominant palette colors from image, sorted by frequency."""
        img = self._get_image(image_path)

        # Scale down for fast color quantization
        thumb = img.copy()
        thumb.thumbnail((160, 160), Image.Resampling.BOX)

        # Quantize to adaptive palette
        # Convert RGBA to RGB with neutral background if necessary
        if thumb.mode == "RGBA":
            bg = Image.new("RGB", thumb.size, (255, 255, 255))
            bg.paste(thumb, mask=thumb.split()[3])
            rgb_thumb = bg
        else:
            rgb_thumb = thumb.convert("RGB")

        p_img = rgb_thumb.convert("P", palette=Image.Palette.ADAPTIVE, colors=max_colors)
        palette = p_img.getpalette() or []
        color_counts = p_img.getcolors() or []

        # Sort by count descending
        sorted_counts = sorted(color_counts, reverse=True)
        total_pixels = sum(c[0] for c in sorted_counts) or 1

        palette_list: list[dict[str, Any]] = []
        seen_hex: set[str] = set()

        for count, idx in sorted_counts:
            offset = idx * 3
            if offset + 3 <= len(palette):
                r, g, b = palette[offset], palette[offset + 1], palette[offset + 2]
                hex_str = rgb_to_hex(r, g, b)
                if hex_str in seen_hex:
                    continue
                seen_hex.add(hex_str)

                percentage = round((count / total_pixels) * 100, 1)
                color_info = build_color_bundle(r, g, b, a=255)
                color_info["percentage"] = percentage
                color_info["css_var"] = f"--color-palette-{len(palette_list) + 1}: {hex_str};"
                palette_list.append(color_info)

                if len(palette_list) >= max_colors:
                    break

        return palette_list
