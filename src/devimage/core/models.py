"""Core data models for DevImage."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

from devimage.core.types import TaskStatus, ToolType


class ImageMetadata(BaseModel):
    """Extracted metadata of an image file."""

    width: int = Field(ge=0, description="Image width in pixels")
    height: int = Field(ge=0, description="Image height in pixels")
    format: str = Field(default="", description="Image format (PNG, JPEG, WEBP, etc.)")
    mode: str = Field(default="RGB", description="Pillow color mode (RGB, RGBA, L, CMYK, etc.)")
    file_size_bytes: int = Field(ge=0, default=0, description="File size in bytes")
    has_transparency: bool = Field(default=False, description="Whether alpha channel exists")
    dpi: tuple[float, float] | None = Field(default=None, description="Image DPI resolution")

    @property
    def aspect_ratio(self) -> float:
        """Return width / height aspect ratio, or 1.0 if height is 0."""
        return (self.width / self.height) if self.height > 0 else 1.0


class ImageItem(BaseModel):
    """Represents an image item loaded in the application workspace or queue."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_path: str = Field(description="Absolute path to the image file")
    file_name: str = Field(default="", description="Base file name")
    file_size: int = Field(ge=0, default=0, description="File size in bytes")
    width: int = Field(ge=0, default=0)
    height: int = Field(ge=0, default=0)
    format: str = Field(default="")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    progress: float = Field(ge=0.0, le=100.0, default=0.0)
    output_path: str | None = None
    error_message: str | None = None

    def model_post_init(self, __context: Any) -> None:
        """Derive file_name if not provided."""
        if not self.file_name and self.file_path:
            import os

            self.file_name = os.path.basename(self.file_path)


class ToolCardInfo(BaseModel):
    """Specification of an interactive tool card for the Home grid."""

    id: ToolType = Field(description="Unique tool identifier")
    name: str = Field(description="Display title of the tool")
    description: str = Field(description="Short subtitle explaining tool capability")
    category: str = Field(description="Category group: image, developer, ai")
    icon: str = Field(description="Icon resource name")
    is_external_ai: bool = Field(default=False, description="Requires remote AI API consent")


class ToastNotification(BaseModel):
    """Toast popup notification model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = Field(default="info", description="Notification severity: info, success, warning, error")
    title: str = Field(description="Headline message")
    message: str = Field(default="", description="Detailed explanation")
    duration_ms: int = Field(default=3000, description="Display duration in milliseconds")
