"""Unit tests for the Image Inspector service and PySide6 controller bridge."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image
from PySide6.QtGui import QGuiApplication

from devimage.core.errors import FileNotFoundAppError
from devimage.core.signals import AppSignalBridge
from devimage.tools.inspector.controller import InspectorController
from devimage.tools.inspector.service import (
    InspectorService,
    calculate_aspect_ratio_str,
    format_file_size,
)


@pytest.fixture
def sample_png_rgba(tmp_path: Path) -> Path:
    """Create a temporary RGBA PNG image with transparency."""
    img_path = tmp_path / "transparent_sample.png"
    img = Image.new("RGBA", (800, 600), (255, 0, 0, 128))
    img.save(img_path, format="PNG")
    return img_path


@pytest.fixture
def sample_jpeg_exif(tmp_path: Path) -> Path:
    """Create a temporary JPEG with DPI and basic EXIF."""
    img_path = tmp_path / "photo_sample.jpg"
    img = Image.new("RGB", (1920, 1080), (100, 150, 200))
    exif = img.getexif()
    # 0x010F = Make, 0x0110 = Model, 0x0131 = Software
    exif[0x010F] = "DevImageCamera"
    exif[0x0110] = "Model-X"
    exif[0x0131] = "DevImage Test Suite"
    img.save(img_path, format="JPEG", exif=exif, dpi=(300, 300))
    return img_path


class TestInspectorService:
    """Tests for pure-Python InspectorService."""

    def test_format_file_size(self) -> None:
        assert format_file_size(500) == "500 B"
        assert format_file_size(1024) == "1.00 KB"
        assert format_file_size(1024 * 1024 * 3) == "3.00 MB"

    def test_calculate_aspect_ratio_str(self) -> None:
        assert "16:9" in calculate_aspect_ratio_str(1920, 1080)
        assert "4:3" in calculate_aspect_ratio_str(800, 600)
        assert "1:1" in calculate_aspect_ratio_str(500, 500)
        assert calculate_aspect_ratio_str(0, 0) == "Unknown"

    def test_file_not_found(self, tmp_path: Path) -> None:
        service = InspectorService()
        with pytest.raises(FileNotFoundAppError):
            service.inspect(tmp_path / "non_existent.png")

    def test_inspect_png_rgba(self, sample_png_rgba: Path) -> None:
        service = InspectorService()
        data = service.inspect(sample_png_rgba)

        assert data["file_name"] == "transparent_sample.png"
        assert data["format"] == "PNG"
        assert data["width"] == 800
        assert data["height"] == 600
        assert data["dimensions"] == "800 × 600"
        assert data["color_mode"] == "RGBA"
        assert data["has_alpha"] is True
        assert data["file_size_bytes"] > 0
        assert "4:3" in data["aspect_ratio"]
        assert len(data["optimization_tips"]) > 0

    def test_inspect_jpeg_exif(self, sample_jpeg_exif: Path) -> None:
        service = InspectorService()
        data = service.inspect(sample_jpeg_exif)

        assert data["file_name"] == "photo_sample.jpg"
        assert data["format"] == "JPEG"
        assert data["width"] == 1920
        assert data["height"] == 1080
        assert data["color_mode"] == "RGB"
        assert data["has_alpha"] is False
        assert data["has_exif"] is True
        assert data["exif_count"] >= 3
        assert data["exif_tags"].get("Make") == "DevImageCamera"
        assert data["exif_tags"].get("Model") == "Model-X"
        assert "300.0" in data["dpi"]

    def test_to_json_and_clipboard_text(self, sample_png_rgba: Path) -> None:
        service = InspectorService()
        data = service.inspect(sample_png_rgba)

        json_str = service.to_json(data)
        parsed = json.loads(json_str)
        assert parsed["file_name"] == "transparent_sample.png"

        report_str = service.to_clipboard_text(data)
        assert "=== DevImage Inspector Report" in report_str
        assert "transparent_sample.png" in report_str
        assert "800 × 600" in report_str


class TestInspectorController:
    """Tests for PySide6 InspectorController bridge."""

    def test_controller_initial_state(self) -> None:
        controller = InspectorController()
        assert controller.currentPath == ""
        assert controller.hasData is False
        assert controller.fileName == ""
        assert controller.dimensions == ""
        assert controller.hasAlpha is False
        assert controller.hasExif is False

    def test_controller_load_image(self, sample_jpeg_exif: Path, qapp: QGuiApplication) -> None:
        signals = AppSignalBridge()
        controller = InspectorController(signals=signals)

        controller.loadImage(str(sample_jpeg_exif))
        assert controller.hasData is True
        assert controller.currentPath == str(sample_jpeg_exif)
        assert controller.fileName == "photo_sample.jpg"
        assert controller.dimensions == "1920 × 1080"
        assert controller.colorMode == "RGB"
        assert controller.hasAlpha is False
        assert controller.hasExif is True
        assert controller.exifCount >= 3
        assert len(controller.exifList) >= 3
        assert len(controller.optimizationTips) > 0

    def test_controller_copy_actions(self, sample_png_rgba: Path, qapp: QGuiApplication) -> None:
        signals = AppSignalBridge()
        controller = InspectorController(signals=signals)
        controller.loadImage(str(sample_png_rgba))

        # Test copyJson
        controller.copyJson()
        clipboard_text = QGuiApplication.clipboard().text()
        assert "transparent_sample.png" in clipboard_text

        # Test copyAll
        controller.copyAll()
        clipboard_report = QGuiApplication.clipboard().text()
        assert "=== DevImage Inspector Report" in clipboard_report

    def test_controller_reset_on_empty_path(
        self, sample_png_rgba: Path, qapp: QGuiApplication
    ) -> None:
        controller = InspectorController()
        controller.loadImage(str(sample_png_rgba))
        assert controller.hasData is True

        controller.loadImage("")
        assert controller.hasData is False
        assert controller.currentPath == ""
        assert controller.dimensions == ""
