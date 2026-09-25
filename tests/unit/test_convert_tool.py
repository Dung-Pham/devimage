"""Unit tests for DevImage Convert service, controller, and QML integration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from PIL import Image
from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication

from devimage.app.application import DevImageApp
from devimage.app.settings import SettingsManager
from devimage.core.errors import (
    FileNotFoundAppError,
    InvalidParameterError,
    UnsupportedFormatError,
)
from devimage.core.signals import AppSignalBridge
from devimage.tools.convert.controller import ConvertController
from devimage.tools.convert.service import (
    ConvertOptions,
    ConvertResult,
    ConvertService,
)


@pytest.fixture
def sample_rgba_png(tmp_path: Path) -> Path:
    """Create a sample RGBA PNG test image with transparency."""
    img_path = tmp_path / "transparent_sample.png"
    img = Image.new("RGBA", (400, 300), color=(255, 0, 0, 128))
    img.save(img_path, format="PNG")
    return img_path


@pytest.fixture
def sample_jpg(tmp_path: Path) -> Path:
    """Create a sample RGB JPEG test image."""
    img_path = tmp_path / "sample_card.jpg"
    img = Image.new("RGB", (500, 500), color=(30, 90, 180))
    img.save(img_path, format="JPEG")
    return img_path


# --- 1. Service Tests ---


def test_convert_service_normalize_format() -> None:
    """Verify target format normalization and validation."""
    service = ConvertService()

    assert service.normalize_target_format("webp") == ("WEBP", ".webp")
    assert service.normalize_target_format("png") == ("PNG", ".png")
    assert service.normalize_target_format("jpeg") == ("JPEG", ".jpg")
    assert service.normalize_target_format("jpg") == ("JPEG", ".jpg")

    with pytest.raises(UnsupportedFormatError):
        service.normalize_target_format("unsupported_fmt")


def test_convert_service_execute_rgba_to_jpeg(sample_rgba_png: Path, tmp_path: Path) -> None:
    """Verify converting RGBA PNG to JPEG flattens transparency over background without error."""
    service = ConvertService()
    dest = tmp_path / "flattened.jpg"

    opts = ConvertOptions(target_format="jpeg", quality=85)
    res: ConvertResult = service.execute(
        input_path=sample_rgba_png,
        output_path=dest,
        options=opts,
    )

    assert res.success is True
    assert res.target_format == "JPEG"
    assert Path(res.output_path).is_file()

    with Image.open(dest) as out_img:
        assert out_img.format == "JPEG"
        assert out_img.mode == "RGB"
        assert out_img.size == (400, 300)


def test_convert_service_execute_jpg_to_webp(sample_jpg: Path, tmp_path: Path) -> None:
    """Verify converting JPEG to WebP format."""
    service = ConvertService()
    dest = tmp_path / "modern.webp"

    opts = ConvertOptions(target_format="webp", quality=80)
    res = service.execute(input_path=sample_jpg, output_path=dest, options=opts)

    assert res.success is True
    assert res.target_format == "WEBP"
    assert dest.is_file()

    with Image.open(dest) as out_img:
        assert out_img.format == "WEBP"
        assert out_img.size == (500, 500)


def test_convert_service_invalid_quality(sample_jpg: Path) -> None:
    """Verify invalid quality raises InvalidParameterError."""
    service = ConvertService()

    with pytest.raises(InvalidParameterError):
        service.execute(sample_jpg, options=ConvertOptions(quality=0))

    with pytest.raises(InvalidParameterError):
        service.execute(sample_jpg, options=ConvertOptions(quality=105))


def test_convert_service_missing_file(tmp_path: Path) -> None:
    """Verify missing file raises FileNotFoundAppError."""
    service = ConvertService()
    missing = tmp_path / "not_there.webp"

    with pytest.raises(FileNotFoundAppError):
        service.execute(missing)


def test_convert_service_batch(sample_rgba_png: Path, sample_jpg: Path, tmp_path: Path) -> None:
    """Verify batch format conversion."""
    service = ConvertService()
    out_dir = tmp_path / "batch_converted"
    out_dir.mkdir()

    files = [sample_rgba_png, sample_jpg]
    opts = ConvertOptions(target_format="webp")

    results = service.execute_batch(input_paths=files, output_dir=out_dir, options=opts)
    assert len(results) == 2
    assert all(r.success for r in results)
    assert all(Path(r.output_path).suffix == ".webp" for r in results)


# --- 2. Controller Tests ---


def test_convert_controller_lifecycle(qtbot: Any, sample_rgba_png: Path) -> None:
    """Verify ConvertController state transitions, format changes, and async execution."""
    signals = AppSignalBridge()
    settings = SettingsManager()
    service = ConvertService()

    ctrl = ConvertController(service=service, signals=signals, settings=settings)

    assert ctrl.hasImage is False
    assert ctrl.originalFormat == ""

    # 1. Load Image
    with qtbot.waitSignal(ctrl.imageChanged, timeout=1000):
        ctrl.loadImage(str(sample_rgba_png))

    assert ctrl.hasImage is True
    assert ctrl.originalFormat.upper() == "PNG"
    assert ctrl.targetFormat == "webp"
    assert ctrl.outputFilename.endswith(".webp")

    # 2. Change Target Format
    with qtbot.waitSignal(ctrl.optionsChanged, timeout=1000):
        ctrl.setTargetFormat("jpeg")

    assert ctrl.targetFormat == "jpeg"
    assert ctrl.outputFilename.endswith(".jpg")

    # 3. Change Quality
    with qtbot.waitSignal(ctrl.optionsChanged, timeout=1000):
        ctrl.setQuality(88)

    assert ctrl.quality == 88

    # 4. Async Execution
    finished_outputs: list[str] = []
    ctrl.convertFinished.connect(lambda t_id, out: finished_outputs.append(out))

    with qtbot.waitSignal(ctrl.convertFinished, timeout=5000):
        task_id = ctrl.executeConvert()
        assert task_id.startswith("task-convert")

    assert len(finished_outputs) == 1
    assert Path(finished_outputs[0]).is_file()
    assert ctrl.isProcessing is False
    assert ctrl.lastOutputPath == finished_outputs[0]


# --- 3. QML Integration Tests ---


def test_qml_app_convert_integration(sample_rgba_png: Path) -> None:
    """Verify DevImageApp exposes convertController and loads ConvertTool in QML."""
    app = DevImageApp([])
    assert app.load_qml() is True

    root = app.engine.rootObjects()[0]
    app_shell = root.findChild(QObject, "appShell")
    assert app_shell is not None

    # Verify controller is available
    assert app.convert_controller is not None
    assert app.backend.convertController is app.convert_controller

    # Navigate to convert tool
    app_shell.navigateToTool("convert", "Format Converter")
    QGuiApplication.processEvents()

    assert app_shell.property("currentRoute") == "tool"
    assert app_shell.property("activeToolId") == "convert"

    # Open image
    app.backend.openImageFile(str(sample_rgba_png))
    QGuiApplication.processEvents()

    tool_shell = app_shell.findChild(QObject, "activeToolShell")
    assert tool_shell is not None
    assert tool_shell.property("currentImagePath") == str(sample_rgba_png)

    # Controller should have loaded the image
    assert app.convert_controller.hasImage is True
    assert app.convert_controller.originalFormat.upper() == "PNG"

    for obj in app.engine.rootObjects():
        obj.deleteLater()
    QGuiApplication.processEvents()
