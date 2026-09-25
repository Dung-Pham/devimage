"""Unit tests for DevImage Resize service, controller, and QML integration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from PIL import Image
from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication

from devimage.app.application import DevImageApp
from devimage.app.settings import SettingsManager
from devimage.core.errors import FileNotFoundAppError, InvalidParameterError
from devimage.core.signals import AppSignalBridge
from devimage.tools.resize.controller import ResizeController
from devimage.tools.resize.service import ResizeOptions, ResizeResult, ResizeService


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    """Create a sample 800x600 RGB PNG test image."""
    img_path = tmp_path / "sample_800x600.png"
    img = Image.new("RGB", (800, 600), color=(50, 100, 150))
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_tall_image(tmp_path: Path) -> Path:
    """Create a sample 600x1200 RGB PNG test image."""
    img_path = tmp_path / "sample_tall_600x1200.png"
    img = Image.new("RGB", (600, 1200), color=(150, 80, 50))
    img.save(img_path)
    return img_path


# --- 1. Dimension & Preset Calculation Tests ---


def test_calculate_dimensions_contain_aspect() -> None:
    """Verify contain mode preserves aspect ratio and fits inside bounding box."""
    service = ResizeService()

    # 800x600 in 400x400 box -> 400x300
    w, h = service.calculate_dimensions(
        orig_w=800,
        orig_h=600,
        target_w=400,
        target_h=400,
        keep_aspect=True,
        mode="contain",
    )
    assert (w, h) == (400, 300)

    # 600x1200 in 400x400 box -> 200x400
    w, h = service.calculate_dimensions(
        orig_w=600,
        orig_h=1200,
        target_w=400,
        target_h=400,
        keep_aspect=True,
        mode="contain",
    )
    assert (w, h) == (200, 400)


def test_calculate_dimensions_cover_mode() -> None:
    """Verify cover mode targets exact bounding box for center-cropping."""
    service = ResizeService()

    w, h = service.calculate_dimensions(
        orig_w=800,
        orig_h=600,
        target_w=400,
        target_h=400,
        keep_aspect=True,
        mode="cover",
    )
    assert (w, h) == (400, 400)


def test_calculate_dimensions_stretch_mode() -> None:
    """Verify stretch mode applies exact target dimensions ignoring aspect."""
    service = ResizeService()

    w, h = service.calculate_dimensions(
        orig_w=800,
        orig_h=600,
        target_w=350,
        target_h=250,
        keep_aspect=False,
        mode="stretch",
    )
    assert (w, h) == (350, 250)


def test_calculate_dimensions_dont_enlarge() -> None:
    """Verify upscale prevention clamps dimensions to original bounds."""
    service = ResizeService()

    # Target 1600x1200 on 800x600 image with dont_enlarge=True
    w, h = service.calculate_dimensions(
        orig_w=800,
        orig_h=600,
        target_w=1600,
        target_h=1200,
        keep_aspect=True,
        dont_enlarge=True,
        mode="contain",
    )
    assert (w, h) == (800, 600)


def test_calculate_preset_dimensions() -> None:
    """Verify preset dimensions scale according to the dominant orientation."""
    service = ResizeService()

    # Landscape (800x600) with preset 1600
    w, h = service.calculate_preset(orig_w=800, orig_h=600, preset_max_dim=1600)
    assert (w, h) == (1600, 1200)

    # Portrait (600x1200) with preset 1024
    w, h = service.calculate_preset(orig_w=600, orig_h=1200, preset_max_dim=1024)
    assert (w, h) == (512, 1024)

    # Invalid preset
    with pytest.raises(InvalidParameterError):
        service.calculate_preset(orig_w=800, orig_h=600, preset_max_dim=0)


def test_invalid_dimensions_error() -> None:
    """Verify errors are raised for non-positive dimensions."""
    service = ResizeService()

    with pytest.raises(InvalidParameterError):
        service.calculate_dimensions(orig_w=0, orig_h=100, target_w=100, target_h=100)

    with pytest.raises(InvalidParameterError):
        service.calculate_dimensions(orig_w=100, orig_h=100, target_w=-10, target_h=100)


# --- 2. Service Execution Tests ---


def test_resize_service_execute(sample_image: Path, tmp_path: Path) -> None:
    """Verify synchronous execution creates valid resized output file."""
    service = ResizeService()
    dest = tmp_path / "output_resized.png"

    opts = ResizeOptions(target_width=400, target_height=300, mode="contain")

    progress_log: list[float] = []

    def on_progress(pct: float, msg: str) -> None:
        progress_log.append(pct)

    res: ResizeResult = service.execute(
        input_path=sample_image,
        output_path=dest,
        options=opts,
        progress_callback=on_progress,
    )

    assert res.success is True
    assert res.original_width == 800
    assert res.original_height == 600
    assert res.target_width == 400
    assert res.target_height == 300
    assert Path(res.output_path).is_file()
    assert len(progress_log) >= 3
    assert progress_log[-1] == 100.0

    # Verify actual image on disk
    with Image.open(dest) as out_img:
        assert out_img.size == (400, 300)


def test_resize_service_missing_file(tmp_path: Path) -> None:
    """Verify error raised on non-existent input file."""
    service = ResizeService()
    missing = tmp_path / "not_there.png"

    with pytest.raises(FileNotFoundAppError):
        service.execute(missing)


def test_resize_service_batch_and_cancel(
    sample_image: Path, sample_tall_image: Path, tmp_path: Path
) -> None:
    """Verify batch resizing executes and honors cancellation."""
    service = ResizeService()
    out_dir = tmp_path / "batch_out"
    out_dir.mkdir()

    files = [sample_image, sample_tall_image]
    opts = ResizeOptions(target_width=300, target_height=300, mode="contain")

    results = service.execute_batch(input_paths=files, output_dir=out_dir, options=opts)
    assert len(results) == 2
    assert all(r.success for r in results)

    # Test cancellation after first item
    cancelled_results = service.execute_batch(
        input_paths=files,
        output_dir=out_dir,
        options=opts,
        cancel_check=lambda: True,
    )
    assert len(cancelled_results) == 0


# --- 3. Controller Tests ---


def test_resize_controller_lifecycle(qtbot: Any, sample_image: Path) -> None:
    """Verify ResizeController properties, aspect ratio locking, and async execution."""
    signals = AppSignalBridge()
    settings = SettingsManager()
    service = ResizeService()

    ctrl = ResizeController(service=service, signals=signals, settings=settings)

    assert ctrl.hasImage is False
    assert ctrl.originalWidth == 0
    assert ctrl.originalHeight == 0

    # 1. Load image
    with qtbot.waitSignal(ctrl.dimensionsChanged, timeout=1000):
        ctrl.loadImage(str(sample_image))

    assert ctrl.hasImage is True
    assert ctrl.originalWidth == 800
    assert ctrl.originalHeight == 600
    assert ctrl.targetWidth == 800
    assert ctrl.targetHeight == 600
    assert ctrl.keepAspect is True

    # 2. Modify target width with aspect locked
    with qtbot.waitSignal(ctrl.dimensionsChanged, timeout=1000):
        ctrl.setTargetWidth(400)

    assert ctrl.targetWidth == 400
    assert ctrl.targetHeight == 300  # 400 / (800/600)

    # 3. Modify target height with aspect locked
    with qtbot.waitSignal(ctrl.dimensionsChanged, timeout=1000):
        ctrl.setTargetHeight(150)

    assert ctrl.targetHeight == 150
    assert ctrl.targetWidth == 200

    # 4. Apply preset
    with qtbot.waitSignal(ctrl.dimensionsChanged, timeout=1000):
        ctrl.applyPreset(1200)

    assert ctrl.targetWidth == 1200
    assert ctrl.targetHeight == 900

    # 5. Unlock aspect ratio
    ctrl.setKeepAspect(False)
    assert ctrl.keepAspect is False

    with qtbot.waitSignal(ctrl.dimensionsChanged, timeout=1000):
        ctrl.setTargetWidth(500)
    assert ctrl.targetWidth == 500
    assert ctrl.targetHeight == 900  # Height remains unchanged

    # 6. Execute async resize
    completed_tasks: list[str] = []
    ctrl.resizeFinished.connect(lambda t_id, path: completed_tasks.append(path))

    with qtbot.waitSignal(ctrl.resizeFinished, timeout=5000):
        task_id = ctrl.executeResize()
        assert task_id.startswith("task-resize")

    assert len(completed_tasks) == 1
    assert Path(completed_tasks[0]).is_file()
    assert ctrl.isProcessing is False
    assert ctrl.lastOutputPath == completed_tasks[0]


# --- 4. QML Integration Tests ---


def test_qml_app_resize_integration(sample_image: Path) -> None:
    """Verify DevImageApp exposes resizeController to QML and loads ResizeTool."""
    app = DevImageApp([])
    loaded = app.load_qml()
    assert loaded is True

    root = app.engine.rootObjects()[0]
    app_shell = root.findChild(QObject, "appShell")
    assert app_shell is not None

    # Verify resizeController is bound and registered
    assert app.resize_controller is not None
    assert app.backend.resizeController is app.resize_controller

    # Navigate to resize tool
    app_shell.navigateToTool("resize", "Resize Image")
    QGuiApplication.processEvents()

    assert app_shell.property("currentRoute") == "tool"
    assert app_shell.property("activeToolId") == "resize"

    # Open image through backend
    app.backend.openImageFile(str(sample_image))
    QGuiApplication.processEvents()

    tool_shell = app_shell.findChild(QObject, "activeToolShell")
    assert tool_shell is not None
    assert tool_shell.property("currentImagePath") == str(sample_image)

    # Verify controller state updated through QML signal linkage
    assert app.resize_controller.hasImage is True
    assert app.resize_controller.originalWidth == 800
    assert app.resize_controller.originalHeight == 600

    for obj in app.engine.rootObjects():
        obj.deleteLater()
    QGuiApplication.processEvents()
