"""Structured error definitions for DevImage.

Conforms to Plan Section 19: All errors displayed to users must be structured with:
- Title
- Description
- Possible cause
- Suggested action
Never expose raw stack traces to the end user.
"""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    """Base structured exception for user-facing errors in DevImage."""

    def __init__(
        self,
        title: str,
        description: str,
        cause: str,
        suggested_action: str,
        details: str = "",
    ) -> None:
        super().__init__(f"{title}: {description}")
        self.title = title
        self.description = description
        self.cause = cause
        self.suggested_action = suggested_action
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        """Serialize error for QML error dialog consumption."""
        return {
            "title": self.title,
            "description": self.description,
            "cause": self.cause,
            "suggested_action": self.suggested_action,
            "details": self.details,
        }


class ImageProcessingError(AppError):
    """Raised when an image transformation fails."""

    def __init__(
        self,
        description: str,
        cause: str = "The selected image file may be corrupt, unsupported, or incomplete.",
        suggested_action: str = "Try using another image file or check file permissions.",
        details: str = "",
    ) -> None:
        super().__init__(
            title="Image Processing Error",
            description=description,
            cause=cause,
            suggested_action=suggested_action,
            details=details,
        )


class UnsupportedFormatError(AppError):
    """Raised when an unrecognized or unsupported file extension is provided."""

    def __init__(self, file_path: str, format_name: str = "") -> None:
        super().__init__(
            title="Unsupported File Format",
            description=f"File '{file_path}' has an unsupported or unreadable format.",
            cause="The format is not in the list of supported extensions (PNG, JPEG, WEBP, BMP, TIFF, GIF, ICO, AVIF).",
            suggested_action="Convert the image to a supported format (PNG, JPEG, WEBP) and try again.",
            details=format_name,
        )


class FileNotFoundAppError(AppError):
    """Raised when an input image file is missing or inaccessible."""

    def __init__(self, file_path: str) -> None:
        super().__init__(
            title="File Not Found",
            description=f"The specified file could not be found: {file_path}",
            cause="The file may have been moved, renamed, or deleted.",
            suggested_action="Please re-select the file using the file picker.",
            details=file_path,
        )


class InvalidParameterError(AppError):
    """Raised when tool options (dimensions, quality, ratio) are invalid."""

    def __init__(self, parameter_name: str, reason: str) -> None:
        super().__init__(
            title="Invalid Parameter",
            description=f"Parameter '{parameter_name}' is invalid: {reason}",
            cause="The provided setting is outside the accepted range.",
            suggested_action="Adjust the setting to a valid value and retry.",
            details=f"{parameter_name}: {reason}",
        )
