"""Unit tests for DevImage Compress service, controller, and QML integration."""

from __future__ import annotations

import os
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
from devimage.tools.compress.controller import CompressController
from devimage.tools.compress.service import (
    CompressOptions,
    CompressResult,
    CompressService,
)


@pytest.fixture
def sample_jpeg(tmp_path: Path) -> Path:
    """Create an uncompressed high-quality JPEG test image."""
    img_path = tmp_path / "sample_photo.jpg"
    img = Image.new("RGB", (1200, 800), color=(120, 160, 200))
    # Draw some varied pixel patterns to make compressibility realistic
    for x in range(0, 1200, 20):
        for y in range(0, 800, 20):
            img.putpixel((x, y), ((x * 3) % 255, (y * 5) % 255, (x + y) % 255))
    img.save(img_path, format="JPEG", quality=100)
    return img_path


@pytest.fixture
def sample_png(tmp_path: Path) -> Path:
    """Create a sample PNG test image."""
    img_path = tmp_path / "sample_graphics.png"
    img = Image.new("RGBA", (600, 600), color=(200, 100, 50, 255))
    img.save(img_path, format="PNG")
    return img_path


# --- 1. Service Tests ---


def test_compress_service_format_resolution(sample_jpeg: Path, sample_png: Path) -> None:
    """Verify format resolution matches input extension or target override."""
    service = CompressService()

    assert service.resolve_format(sample_jpeg, "original") == "JPEG"
    assert service.resolve_format(sample_png, "original") == "PNG"
    assert service.resolve_format(sample_jpeg, "webp") == "WEBP"
    assert service.resolve_format(sample_png, "jpeg") == "JPEG"


def test_compress_service_estimate(sample_jpeg: Path) -> None:
    """Verify in-memory compression estimation without touching disk."""
    service = CompressService()
    orig_size = os.path.getsize(sample_jpeg)

    opts = CompressOptions(quality=60, target_format="jpeg")
    est_size, reduction = service.estimate_compression(sample_jpeg, opts)

    assert est_size > 0
    assert est_size < orig_size
    assert reduction > 0.0


def test_compress_service_execute_jpeg(sample_jpeg: Path, tmp_path: Path) -> None:
    """Verify JPEG compression reduces file size and saves correctly."""
    service = CompressService()
    dest = tmp_path / "compressed_output.jpg"

    opts = CompressOptions(quality=50, target_format="jpeg", strip_metadata=True)
    res: CompressResult = service.execute(
        input_path=sample_jpeg,
        output_path=dest,
        options=opts,
    )

    assert res.success is True
    assert res.compressed_size_bytes < res.original_size_bytes
    assert res.reduction_percent > 0.0
    assert Path(res.output_path).is_file()

    with Image.open(dest) as img:
        assert img.size == (1200, 800)


def test_compress_service_webp_conversion(sample_jpeg: Path, tmp_path: Path) -> None:
    """Verify compressing with WebP format produces valid WebP output."""
    service = CompressService()
    dest = tmp_path / "converted.webp"

    opts = CompressOptions(quality=70, target_format="webp")
    res = service.execute(input_path=sample_jpeg, output_path=dest, options=opts)

    assert res.success is True
    assert res.format_name == "WEBP"
    assert dest.suffix == ".webp"
    assert dest.is_file()


def test_compress_service_invalid_quality(sample_jpeg: Path) -> None:
    """Verify exception raised for invalid quality outside 1-100."""
    service = CompressService()

    with pytest.raises(InvalidParameterError):
        service.execute(sample_jpeg, options=CompressOptions(quality=0))

    with pytest.raises(InvalidParameterError):
        service.execute(sample_jpeg, options=CompressOptions(quality=120))


def test_compress_service_missing_file(tmp_path: Path) -> None:
    """Verify exception raised for non-existent input file."""
    service = CompressService()
    missing = tmp_path / "ghost.jpg"

    with pytest.raises(FileNotFoundAppError):
        service.execute(missing)


def test_compress_service_batch(sample_jpeg: Path, sample_png: Path, tmp_path: Path) -> None:
    """Verify batch compression on multiple files."""
    service = CompressService()
    out_dir = tmp_path / "batch_compressed"
    out_dir.mkdir()

    files = [sample_jpeg, sample_png]
    opts = CompressOptions(quality=65)

    results = service.execute_batch(input_paths=files, output_dir=out_dir, options=opts)
    assert len(results) == 2
    assert all(r.success for r in results)


# --- 2. Controller Tests ---


def test_compress_controller_lifecycle(qtbot: Any, sample_jpeg: Path) -> None:
    """Verify CompressController state transitions, quality updates, and async worker execution."""
    signals = AppSignalBridge()
    settings = SettingsManager()
    service = CompressService()

    ctrl = CompressController(service=service, signals=signals, settings=settings)

    assert ctrl.hasImage is False
    assert ctrl.originalSizeBytes == 0

    # 1. Load Image
    with qtbot.waitSignal(ctrl.imageChanged, timeout=1000):
        ctrl.loadImage(str(sample_jpeg))

    assert ctrl.hasImage is True
    assert ctrl.originalSizeBytes > 0
    assert "KB" in ctrl.originalSizeText or "MB" in ctrl.originalSizeText

    # 2. Update Quality
    with qtbot.waitSignal(ctrl.optionsChanged, timeout=1000):
        ctrl.setQuality(50)

    assert ctrl.quality == 50
    assert ctrl.estimatedSizeBytes > 0
    assert ctrl.estimatedReduction > 0.0

    # 3. Change Target Format
    with qtbot.waitSignal(ctrl.optionsChanged, timeout=1000):
        ctrl.setTargetFormat("webp")

    assert ctrl.targetFormat == "webp"

    # 4. Async Execution
    finished_outputs: list[str] = []
    ctrl.compressFinished.connect(lambda t_id, out: finished_outputs.append(out))

    with qtbot.waitSignal(ctrl.compressFinished, timeout=5000):
        task_id = ctrl.executeCompress()
        assert task_id.startswith("task-compress")

    assert len(finished_outputs) == 1
    assert Path(finished_outputs[0]).is_file()
    assert ctrl.isProcessing is False
    assert ctrl.lastOutputPath == finished_outputs[0]


# --- 3. QML Integration Tests ---


def test_qml_app_compress_integration(sample_jpeg: Path) -> None:
    """Verify DevImageApp exposes compressController and loads CompressTool in QML."""
    app = DevImageApp([])
    assert app.load_qml() is True

    root = app.engine.rootObjects()[0]
    app_shell = root.findChild(QObject, "appShell")
    assert app_shell is not None

    # Verify controller is available
    assert app.compress_controller is not None
    assert app.backend.compressController is app.compress_controller

    # Navigate to compress tool
    app_shell.navigateToTool("compress", "Compress Image")
    QGuiApplication.processEvents()

    assert app_shell.property("currentRoute") == "tool"
    assert app_shell.property("activeToolId") == "compress"

    # Open image
    app.backend.openImageFile(str(sample_jpeg))
    QGuiApplication.processEvents()

    tool_shell = app_shell.findChild(QObject, "activeToolShell")
    assert tool_shell is not None
    assert tool_shell.property("currentImagePath") == str(sample_jpeg)

    # Controller should have loaded the image
    assert app.compress_controller.hasImage is True
    assert app.compress_controller.originalSizeBytes > 0

    for obj in app.engine.rootObjects():
        obj.deleteLater()
    QGuiApplication.processEvents()
