"""Unit tests for core models, types, errors, and signal bridge."""

from devimage.core.errors import (
    AppError,
    FileNotFoundAppError,
    ImageProcessingError,
    InvalidParameterError,
    UnsupportedFormatError,
)
from devimage.core.models import ImageItem, ImageMetadata, ToastNotification, ToolCardInfo
from devimage.core.signals import AppSignalBridge
from devimage.core.types import ImageFormat, TaskStatus, ThemeMode, ToolType


def test_core_types():
    """Verify enum members and values."""
    assert ImageFormat.PNG.value == "PNG"
    assert ImageFormat.JPEG.value == "JPEG"
    assert ToolType.RESIZE.value == "resize"
    assert ToolType.REMOVE_BACKGROUND.value == "remove_background"
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.COMPLETED.value == "completed"
    assert ThemeMode.DARK.value == "dark"


def test_app_error_structure():
    """Verify AppError conforms to Title, Description, Cause, Suggested Action."""
    err = AppError(
        title="Sample Title",
        description="Sample Description",
        cause="Sample Cause",
        suggested_action="Sample Action",
        details="Technical details",
    )
    d = err.to_dict()
    assert d["title"] == "Sample Title"
    assert d["description"] == "Sample Description"
    assert d["cause"] == "Sample Cause"
    assert d["suggested_action"] == "Sample Action"
    assert d["details"] == "Technical details"


def test_derived_errors():
    """Verify specific derived error types."""
    err1 = ImageProcessingError("Corrupted header")
    assert err1.title == "Image Processing Error"

    err2 = UnsupportedFormatError("/path/to/img.xyz", "XYZ")
    assert err2.title == "Unsupported File Format"

    err3 = FileNotFoundAppError("/path/to/missing.png")
    assert err3.title == "File Not Found"

    err4 = InvalidParameterError("quality", "Must be 1-100")
    assert err4.title == "Invalid Parameter"


def test_image_models():
    """Verify ImageMetadata and ImageItem validation and behaviors."""
    meta = ImageMetadata(
        width=1920,
        height=1080,
        format="PNG",
        mode="RGBA",
        has_transparency=True,
    )
    assert meta.width == 1920
    assert meta.aspect_ratio == 1920 / 1080

    item = ImageItem(file_path="C:/photos/vacation.jpg", width=800, height=600)
    assert item.file_name == "vacation.jpg"
    assert item.status == TaskStatus.PENDING
    assert item.progress == 0.0


def test_tool_card_and_toast():
    """Verify ToolCardInfo and ToastNotification schemas."""
    card = ToolCardInfo(
        id=ToolType.RESIZE,
        name="Resize",
        description="Scale dimensions",
        category="image",
        icon="resize.svg",
    )
    assert card.id == ToolType.RESIZE
    assert not card.is_external_ai

    toast = ToastNotification(
        type="success",
        title="Saved",
        message="Image saved to disk",
    )
    assert toast.type == "success"
    assert toast.duration_ms == 3000


def test_signal_bridge(qtbot):
    """Verify Qt signal bridge emissions and slot invocations."""
    bridge = AppSignalBridge()

    # 1. Test toast notification signal
    toasts_received = []
    bridge.notify.connect(lambda t, h, m, d: toasts_received.append((t, h, m, d)))
    bridge.showToast("info", "Hello", "Welcome to DevImage", 4000)
    assert len(toasts_received) == 1
    assert toasts_received[0] == ("info", "Hello", "Welcome to DevImage", 4000)

    # 2. Test error dialog signal
    errors_received = []
    bridge.errorOccurred.connect(lambda t, d, c, a: errors_received.append((t, d, c, a)))
    bridge.triggerError("Fail", "Failed to load", "Broken file", "Pick another")
    assert len(errors_received) == 1
    assert errors_received[0][0] == "Fail"

    # 3. Test tool activation signal
    tools_received = []
    bridge.toolActivated.connect(lambda tid: tools_received.append(tid))
    bridge.selectTool("resize")
    assert tools_received == ["resize"]
