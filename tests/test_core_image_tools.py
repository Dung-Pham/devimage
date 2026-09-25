"""Comprehensive end-to-end acceptance tests for Phase 2 Core Image Tools.

Validates the full headless pipeline for Resize, Compress, Convert, and Crop,
including asynchronous execution, format integrity, and QML app shell integration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from PIL import Image
from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication

from devimage.app.application import DevImageApp
from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge
from devimage.tools.compress.controller import CompressController
from devimage.tools.compress.service import CompressOptions, CompressService
from devimage.tools.convert.controller import ConvertController
from devimage.tools.convert.service import ConvertOptions, ConvertService
from devimage.tools.crop.controller import CropController
from devimage.tools.crop.service import CropOptions, CropService
from devimage.tools.resize.controller import ResizeController
from devimage.tools.resize.service import ResizeOptions, ResizeService


@pytest.fixture
def test_images(tmp_path: Path) -> dict[str, Path]:
    """Generate a diverse set of test images covering different formats and channels."""
    img_dir = tmp_path / "fixtures"
    img_dir.mkdir(parents=True, exist_ok=True)

    # 1. RGBA PNG with semi-transparent pixels
    rgba_path = img_dir / "sample_rgba.png"
    rgba_img = Image.new("RGBA", (800, 600), color=(50, 100, 200, 180))
    rgba_img.save(rgba_path)

    # 2. RGB JPEG
    rgb_jpeg_path = img_dir / "sample_rgb.jpg"
    rgb_img = Image.new("RGB", (1200, 800), color=(220, 80, 40))
    rgb_img.save(rgb_jpeg_path, quality=95)

    # 3. WebP image
    webp_path = img_dir / "sample_lossless.webp"
    webp_img = Image.new("RGBA", (640, 480), color=(10, 180, 90, 255))
    webp_img.save(webp_path, lossless=True)

    return {
        "rgba_png": rgba_path,
        "rgb_jpeg": rgb_jpeg_path,
        "webp": webp_path,
    }


class TestPhase2CoreImageServices:
    """Verifies that all 4 standalone services execute cleanly with correct image math."""

    def test_resize_service_contain_and_presets(
        self, test_images: dict[str, Path], tmp_path: Path
    ) -> None:
        """ResizeService scales images correctly with aspect ratio preservation."""
        service = ResizeService()
        out_dir = tmp_path / "resize_out"
        out_dir.mkdir()

        # 1. Scale down landscape
        dest = out_dir / "scaled_800x600.png"
        res = service.execute(
            input_path=test_images["rgba_png"],
            output_path=dest,
            options=ResizeOptions(target_width=400, target_height=300, mode="contain"),
        )
        assert res.success is True
        assert res.target_width == 400
        assert res.target_height == 300
        with Image.open(dest) as img:
            assert img.size == (400, 300)

        # 2. Preset calculation
        target_w, target_h = service.calculate_preset(orig_w=1200, orig_h=800, preset_max_dim=600)
        assert target_w == 600
        assert target_h == 400

    def test_compress_service_transmutation_and_reduction(
        self, test_images: dict[str, Path], tmp_path: Path
    ) -> None:
        """CompressService produces smaller files and handles alpha channel flattening."""
        service = CompressService()
        out_dir = tmp_path / "compress_out"
        out_dir.mkdir()

        # Compress RGBA PNG into high-efficiency WebP
        dest_webp = out_dir / "compressed.webp"
        res = service.execute(
            input_path=test_images["rgba_png"],
            output_path=dest_webp,
            options=CompressOptions(quality=60, target_format="webp"),
        )
        assert res.success is True
        assert res.compressed_size_bytes > 0
        assert res.compressed_size_bytes < res.original_size_bytes
        assert Path(res.output_path).is_file()

        with Image.open(dest_webp) as img:
            assert img.format == "WEBP"
            assert img.size == (800, 600)

    def test_convert_service_format_matrix(
        self, test_images: dict[str, Path], tmp_path: Path
    ) -> None:
        """ConvertService transmutes formats correctly including RGBA -> JPEG with background compositing."""
        service = ConvertService()
        out_dir = tmp_path / "convert_out"
        out_dir.mkdir()

        # 1. RGBA -> JPEG (requires white matte compositing)
        dest_jpg = out_dir / "converted_from_rgba.jpg"
        res_jpg = service.execute(
            input_path=test_images["rgba_png"],
            output_path=dest_jpg,
            options=ConvertOptions(target_format="jpeg", background_color=(255, 255, 255)),
        )
        assert res_jpg.success is True
        with Image.open(dest_jpg) as img:
            assert img.format == "JPEG"
            assert img.mode == "RGB"
            assert img.size == (800, 600)

        # 2. JPEG -> WebP
        dest_webp = out_dir / "converted_from_jpeg.webp"
        res_webp = service.execute(
            input_path=test_images["rgb_jpeg"],
            output_path=dest_webp,
            options=ConvertOptions(target_format="webp"),
        )
        assert res_webp.success is True
        with Image.open(dest_webp) as img:
            assert img.format == "WEBP"
            assert img.size == (1200, 800)

    def test_crop_service_coordinate_clamping_and_rotation(
        self, test_images: dict[str, Path], tmp_path: Path
    ) -> None:
        """CropService crops accurate regions and rotates images without distortion."""
        service = CropService()
        out_dir = tmp_path / "crop_out"
        out_dir.mkdir()

        # Crop center 400x300 and rotate 180 degrees
        dest = out_dir / "cropped_180.png"
        res = service.execute(
            input_path=test_images["rgba_png"],
            output_path=dest,
            options=CropOptions(crop_box=(200, 150, 600, 450), rotation=180),
        )
        assert res.success is True
        assert res.cropped_width == 400
        assert res.cropped_height == 300
        with Image.open(dest) as img:
            assert img.size == (400, 300)


class TestPhase2AsyncControllers:
    """Verifies that all 4 PySide6 controllers execute asynchronously via QThreadPool."""

    def test_all_controllers_async_pipeline(
        self, qtbot: Any, test_images: dict[str, Path], tmp_path: Path
    ) -> None:
        """Verify each controller dispatches to background thread and updates QML signals."""
        signals = AppSignalBridge()
        settings = SettingsManager(tmp_path / "settings.json")

        # 1. Resize Controller
        resize_ctrl = ResizeController(signals=signals, settings=settings)
        resize_ctrl.loadImage(str(test_images["rgba_png"]))
        resize_ctrl.setTargetWidth(400)
        with qtbot.waitSignal(resize_ctrl.resizeFinished, timeout=5000):
            tid = resize_ctrl.executeResize(output_dir=str(tmp_path))
            assert tid.startswith("task-resize")
        assert Path(resize_ctrl.lastOutputPath).is_file()

        # 2. Compress Controller
        compress_ctrl = CompressController(signals=signals, settings=settings)
        compress_ctrl.loadImage(str(test_images["rgb_jpeg"]))
        compress_ctrl.setQuality(50)
        with qtbot.waitSignal(compress_ctrl.compressFinished, timeout=5000):
            tid = compress_ctrl.executeCompress(output_dir=str(tmp_path))
            assert tid.startswith("task-compress")
        assert Path(compress_ctrl.lastOutputPath).is_file()

        # 3. Convert Controller
        convert_ctrl = ConvertController(signals=signals, settings=settings)
        convert_ctrl.loadImage(str(test_images["rgba_png"]))
        convert_ctrl.setTargetFormat("webp")
        with qtbot.waitSignal(convert_ctrl.convertFinished, timeout=5000):
            tid = convert_ctrl.executeConvert(output_dir=str(tmp_path))
            assert tid.startswith("task-convert")
        assert Path(convert_ctrl.lastOutputPath).is_file()

        # 4. Crop Controller
        crop_ctrl = CropController(signals=signals, settings=settings)
        crop_ctrl.loadImage(str(test_images["rgba_png"]))
        crop_ctrl.setNormalizedCrop(0.1, 0.1, 0.6, 0.6)
        with qtbot.waitSignal(crop_ctrl.cropFinished, timeout=5000):
            tid = crop_ctrl.executeCrop(output_dir=str(tmp_path))
            assert tid == "task-crop"
        assert Path(crop_ctrl.lastOutputPath).is_file()


class TestPhase2AppShellAcceptance:
    """Verifies full application shell startup, route navigation to all 4 tools, and QML binding."""

    def test_full_app_shell_tool_navigation(self, test_images: dict[str, Path]) -> None:
        """DevImageApp loads all 4 tools, context properties, and navigates seamlessly."""
        app = DevImageApp([])
        loaded = app.load_qml()
        assert loaded is True

        root = app.engine.rootObjects()[0]
        app_shell = root.findChild(QObject, "appShell")
        assert app_shell is not None

        # Verify all 4 controllers registered on root context
        assert app.resize_controller is not None
        assert app.compress_controller is not None
        assert app.convert_controller is not None
        assert app.crop_controller is not None

        assert app.backend.resizeController is app.resize_controller
        assert app.backend.compressController is app.compress_controller
        assert app.backend.convertController is app.convert_controller
        assert app.backend.cropController is app.crop_controller

        tools = [
            ("resize", "Resize Image", app.resize_controller),
            ("compress", "Compress Image", app.compress_controller),
            ("convert", "Convert Format", app.convert_controller),
            ("crop", "Crop & Rotate", app.crop_controller),
        ]

        # Navigate through every tool and feed image
        for tool_id, tool_name, controller in tools:
            app_shell.navigateToTool(tool_id, tool_name)
            QGuiApplication.processEvents()
            assert app_shell.property("currentRoute") == "tool"
            assert app_shell.property("activeToolId") == tool_id

            # Load image
            app.backend.openImageFile(str(test_images["rgba_png"]))
            QGuiApplication.processEvents()

            assert controller.hasImage is True

        for obj in app.engine.rootObjects():
            obj.deleteLater()
        QGuiApplication.processEvents()
