"""Unit and integration tests for the Crop Tool service and PySide6 controller."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from devimage.app.application import DevImageApp
from devimage.app.settings import SettingsManager
from devimage.core.errors import FileNotFoundAppError, InvalidParameterError
from devimage.core.signals import AppSignalBridge
from devimage.tools.crop.controller import CropController
from devimage.tools.crop.service import CropOptions, CropService


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    """Create a temporary test image of size 800x600 with distinct pattern."""
    img_path = tmp_path / "test_crop.png"
    img = Image.new("RGB", (800, 600), color=(100, 150, 200))
    img.save(img_path)
    return img_path


class TestCropService:
    """Tests for the CropService logic and image operations."""

    def test_clamp_box_valid(self) -> None:
        """Valid coordinates within bounds remain unchanged."""
        box = CropService.clamp_box((100, 100, 500, 400), 800, 600)
        assert box == (100, 100, 500, 400)

    def test_clamp_box_out_of_bounds(self) -> None:
        """Coordinates exceeding bounds are clamped cleanly."""
        box = CropService.clamp_box((-50, -20, 1000, 800), 800, 600)
        assert box == (0, 0, 800, 600)

    def test_clamp_box_invalid_raises_error(self) -> None:
        """Inverted coordinates raise InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            CropService.clamp_box((400, 300, 200, 100), 800, 600)

    def test_calculate_center_crop_square_preset(self) -> None:
        """1:1 aspect ratio on 800x600 image creates a centered 600x600 box."""
        left, top, right, bottom = CropService.calculate_center_crop(800, 600, 1, 1)
        assert (right - left) == 600
        assert (bottom - top) == 600
        assert left == 100
        assert top == 0
        assert right == 700
        assert bottom == 600

    def test_calculate_center_crop_4_3_preset(self) -> None:
        """4:3 aspect ratio on 1000x1000 image creates a centered 1000x750 box."""
        left, top, right, bottom = CropService.calculate_center_crop(1000, 1000, 4, 3)
        assert (right - left) == 1000
        assert (bottom - top) == 750
        assert left == 0
        assert top == 125
        assert right == 1000
        assert bottom == 875

    def test_calculate_center_crop_invalid_dimensions(self) -> None:
        """Zero or negative values raise InvalidParameterError."""
        with pytest.raises(InvalidParameterError):
            CropService.calculate_center_crop(0, 100, 1, 1)

    def test_execute_crop_basic(self, sample_image: Path, tmp_path: Path) -> None:
        """Execute standard crop and verify output dimensions."""
        service = CropService()
        out_file = tmp_path / "output_cropped.png"

        progress_records: list[tuple[float, str]] = []

        def on_progress(pct: float, msg: str) -> None:
            progress_records.append((pct, msg))

        opts = CropOptions(
            crop_box=(100, 100, 500, 400),
            rotation=0,
            quality=90,
        )

        result = service.execute(
            str(sample_image),
            output_path=str(out_file),
            options=opts,
            progress_callback=on_progress,
        )

        assert result.success is True
        assert result.original_width == 800
        assert result.original_height == 600
        assert result.cropped_width == 400
        assert result.cropped_height == 300
        assert Path(result.output_path).is_file()
        assert len(progress_records) > 0

        with Image.open(result.output_path) as out_img:
            assert out_img.size == (400, 300)

    def test_execute_crop_with_rotation(self, sample_image: Path, tmp_path: Path) -> None:
        """Execute crop combined with 90-degree clockwise rotation."""
        service = CropService()
        opts = CropOptions(
            crop_box=(0, 0, 400, 200),
            rotation=90,
        )

        result = service.execute(
            str(sample_image),
            output_path=str(tmp_path / "rotated.png"),
            options=opts,
        )

        assert result.success is True
        # Rotated 90 deg -> 600x800, then cropped with (0, 0, 400, 200) -> 400x200
        assert result.cropped_width == 400
        assert result.cropped_height == 200

        with Image.open(result.output_path) as out_img:
            assert out_img.size == (400, 200)

    def test_execute_missing_file_raises_error(self, tmp_path: Path) -> None:
        """Attempting to crop a non-existent file raises FileNotFoundAppError."""
        service = CropService()
        with pytest.raises(FileNotFoundAppError):
            service.execute(str(tmp_path / "nonexistent.png"))


class TestCropController:
    """Tests for the PySide6 QObject CropController."""

    def test_initial_state(self) -> None:
        """Controller initializes with default uncropped state and aspect presets."""
        ctrl = CropController()
        assert ctrl.currentFilePath == ""
        assert ctrl.hasImage is False
        assert ctrl.originalWidth == 0
        assert ctrl.originalHeight == 0
        assert ctrl.cropX == 0.0
        assert ctrl.cropY == 0.0
        assert ctrl.cropWidth == 1.0
        assert ctrl.cropHeight == 1.0
        assert ctrl.aspectRatioMode == "free"
        assert ctrl.rotation == 0
        assert ctrl.isProcessing is False

    def test_load_image(self, sample_image: Path) -> None:
        """Loading an image inspects dimensions and resets crop rect."""
        ctrl = CropController()
        ctrl.loadImage(str(sample_image))

        assert ctrl.hasImage is True
        assert ctrl.originalWidth == 800
        assert ctrl.originalHeight == 600
        assert ctrl.cropWidth == 1.0
        assert ctrl.cropHeight == 1.0

    def test_set_crop_rect_normalized(self, sample_image: Path) -> None:
        """Setting normalized coordinates clamps within [0, 1]."""
        ctrl = CropController()
        ctrl.loadImage(str(sample_image))

        ctrl.setNormalizedCrop(0.1, 0.2, 0.5, 0.4)
        assert pytest.approx(ctrl.cropX) == 0.1
        assert pytest.approx(ctrl.cropY) == 0.2
        assert pytest.approx(ctrl.cropWidth) == 0.5
        assert pytest.approx(ctrl.cropHeight) == 0.4

        assert ctrl.pixelCropWidth == 400
        assert ctrl.pixelCropHeight == 240

    def test_set_aspect_ratio_preset(self, sample_image: Path) -> None:
        """Applying aspect preset centers the crop box according to ratio."""
        ctrl = CropController()
        ctrl.loadImage(str(sample_image))  # 800x600

        ctrl.setAspectRatioMode("1:1")
        assert ctrl.aspectRatioMode == "1:1"
        assert ctrl.pixelCropWidth == 600
        assert ctrl.pixelCropHeight == 600
        assert pytest.approx(ctrl.cropX) == 100 / 800
        assert pytest.approx(ctrl.cropY) == 0.0

    def test_rotation_controls(self, sample_image: Path) -> None:
        """Rotating adjusts angle and swaps width/height accordingly."""
        ctrl = CropController()
        ctrl.loadImage(str(sample_image))  # 800x600

        ctrl.rotateClockwise()
        assert ctrl.rotation == 90
        assert ctrl.currentWidth == 600
        assert ctrl.currentHeight == 800

        ctrl.rotateClockwise()
        assert ctrl.rotation == 180
        assert ctrl.currentWidth == 800
        assert ctrl.currentHeight == 600

        ctrl.rotateCounterClockwise()
        assert ctrl.rotation == 90

        ctrl.resetCrop()
        assert ctrl.rotation == 0
        assert ctrl.currentWidth == 800
        assert ctrl.currentHeight == 600

    def test_execute_crop_async(self, qtbot: Any, sample_image: Path, tmp_path: Path) -> None:
        """Executing crop triggers background worker and fires signals."""
        signals = AppSignalBridge()
        settings = SettingsManager(tmp_path / "settings.json")
        ctrl = CropController(signals=signals, settings=settings)

        ctrl.loadImage(str(sample_image))
        ctrl.setNormalizedCrop(0.25, 0.25, 0.5, 0.5)

        completed_events: list[tuple[str, str]] = []
        ctrl.cropFinished.connect(lambda tid, path: completed_events.append((tid, path)))

        with qtbot.waitSignal(ctrl.cropFinished, timeout=5000):
            task_id = ctrl.executeCrop(output_dir=str(tmp_path))
            assert task_id == "task-crop"

        assert len(completed_events) == 1
        out_path = completed_events[0][1]
        assert Path(out_path).is_file()
        assert ctrl.isProcessing is False
        assert ctrl.lastOutputPath == out_path

        with Image.open(out_path) as out_img:
            assert out_img.size == (400, 300)


class TestCropAppIntegration:
    """Integration test verifying CropController in DevImageApp."""

    def test_app_wires_crop_controller(self) -> None:
        """DevImageApp instantiates and exposes cropController to QML context."""
        app = DevImageApp(["test_app"])
        assert hasattr(app, "crop_controller")
        assert app.crop_controller is not None
        assert app.backend.cropController is app.crop_controller
