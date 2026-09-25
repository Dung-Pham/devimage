"""Core enumeration types for DevImage."""

from enum import Enum


class ImageFormat(str, Enum):
    """Supported image file formats."""

    PNG = "PNG"
    JPEG = "JPEG"
    WEBP = "WEBP"
    BMP = "BMP"
    TIFF = "TIFF"
    GIF = "GIF"
    ICO = "ICO"
    AVIF = "AVIF"


class ToolType(str, Enum):
    """Registered tool identifier keys."""

    # Image Tools
    REMOVE_BACKGROUND = "remove_background"
    RESIZE = "resize"
    COMPRESS = "compress"
    CONVERT = "convert"
    CROP = "crop"

    # Developer Tools
    INSPECTOR = "inspector"
    COLOR_PICKER = "color_picker"
    OCR = "ocr"
    RENAME = "rename"
    COPY_PATH = "copy_path"

    # AI Tools
    ANALYZE = "analyze"
    ALT_TEXT = "alt_text"
    AI_COMMAND = "ai_command"


class TaskStatus(str, Enum):
    """Status lifecycle of background and batch image processing tasks."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ThemeMode(str, Enum):
    """Application visual theme."""

    DARK = "dark"
    LIGHT = "light"
    SYSTEM = "system"
