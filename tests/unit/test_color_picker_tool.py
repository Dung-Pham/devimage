"""Unit tests for ColorService and ColorPickerController."""

from pathlib import Path

import pytest
from PIL import Image
from PySide6.QtGui import QGuiApplication

from devimage.tools.color_picker.controller import ColorPickerController
from devimage.tools.color_picker.service import (
    ColorService,
    get_contrast_color,
    hex_to_rgb,
    rgb_to_hex,
    rgb_to_hsl,
    rgb_to_hsv,
)


@pytest.fixture
def sample_image_path(tmp_path: Path) -> str:
    """Create a sample test image with distinct colored quadrants."""
    img = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    # Quadrant 1 (top-left): Red #FF0000
    for x in range(50):
        for y in range(50):
            img.putpixel((x, y), (255, 0, 0, 255))
    # Quadrant 2 (top-right): Green #00FF00
    for x in range(50, 100):
        for y in range(50):
            img.putpixel((x, y), (0, 255, 0, 255))
    # Quadrant 3 (bottom-left): Blue #0000FF
    for x in range(50):
        for y in range(50, 100):
            img.putpixel((x, y), (0, 0, 255, 255))
    # Quadrant 4 (bottom-right): Yellow #FFFF00
    for x in range(50, 100):
        for y in range(50, 100):
            img.putpixel((x, y), (255, 255, 0, 255))

    file_path = str(tmp_path / "test_palette.png")
    img.save(file_path)
    return file_path


def test_rgb_to_hex():
    """Verify RGB to Hex conversions including alpha and clamping."""
    assert rgb_to_hex(255, 0, 0) == "#FF0000"
    assert rgb_to_hex(0, 255, 0) == "#00FF00"
    assert rgb_to_hex(0, 0, 255) == "#0000FF"
    assert rgb_to_hex(255, 255, 255, 128) == "#FFFFFF80"
    # Clamping out-of-range values
    assert rgb_to_hex(-20, 300, 128) == "#00FF80"


def test_hex_to_rgb():
    """Verify Hex parsing for 3, 4, 6, and 8 character hex strings."""
    assert hex_to_rgb("#FF0000") == (255, 0, 0, 255)
    assert hex_to_rgb("#00FF0080") == (0, 255, 0, 128)
    assert hex_to_rgb("#FFF") == (255, 255, 255, 255)
    assert hex_to_rgb("#0F08") == (0, 255, 0, 136)

    with pytest.raises(ValueError):
        hex_to_rgb("not-a-hex")


def test_rgb_to_hsl_and_hsv():
    """Verify RGB conversion to HSL and HSV color spaces."""
    # Red
    h, s, l_val = rgb_to_hsl(255, 0, 0)
    assert h == 0 and s == 100 and l_val == 50

    # Green
    h, s, l_val = rgb_to_hsl(0, 255, 0)
    assert h == 120 and s == 100 and l_val == 50

    # Blue
    h, s, l_val = rgb_to_hsl(0, 0, 255)
    assert h == 240 and s == 100 and l_val == 50

    # HSV
    h, s, v = rgb_to_hsv(0, 0, 255)
    assert h == 240 and s == 100 and v == 100


def test_contrast_calculation():
    """Verify optimal text contrast color determination."""
    assert get_contrast_color(0, 0, 0) == "#ffffff"  # Dark background -> white text
    assert get_contrast_color(255, 255, 255) == "#000000"  # Bright background -> black text
    assert get_contrast_color(255, 255, 0) == "#000000"  # Yellow -> black text


def test_color_service_sample_pixel(sample_image_path: str):
    """Verify pixel sampling at coordinates within the quadrants."""
    service = ColorService()

    # Sample Red quadrant (20, 20)
    data_red = service.sample_pixel(sample_image_path, 20, 20)
    assert data_red["hex"] == "#FF0000"
    assert data_red["r"] == 255 and data_red["g"] == 0 and data_red["b"] == 0
    assert data_red["rgb_str"] == "rgb(255, 0, 0)"
    assert "--color-sampled: #FF0000;" in data_red["css_var"]

    # Sample Blue quadrant (20, 70)
    data_blue = service.sample_pixel(sample_image_path, 20, 70)
    assert data_blue["hex"] == "#0000FF"
    assert data_blue["b"] == 255

    # Out of bounds clamping should not throw
    data_clamped = service.sample_pixel(sample_image_path, 9999, -50)
    assert data_clamped["x"] == 99
    assert data_clamped["y"] == 0


def test_color_service_extract_palette(sample_image_path: str):
    """Verify extraction of the 4 dominant colors."""
    service = ColorService()
    palette = service.extract_palette(sample_image_path, max_colors=4)

    assert len(palette) >= 4
    hexes = [p["hex"] for p in palette]
    # Should contain all 4 quadrant colors
    assert "#FF0000" in hexes
    assert "#00FF00" in hexes
    assert "#0000FF" in hexes
    assert "#FFFF00" in hexes


def test_color_picker_controller_lifecycle(sample_image_path: str):
    """Verify ColorPickerController signals, properties, and clipboard operations."""
    controller = ColorPickerController()

    assert controller.hasImage is False

    # 1. Load Image
    controller.loadImage(sample_image_path)
    assert controller.hasImage is True
    assert controller.currentImagePath == sample_image_path
    assert len(controller.paletteColors) >= 4

    # 2. Sample specific pixel
    changed_signals = []
    controller.colorChanged.connect(lambda: changed_signals.append(True))
    controller.sampleAt(10, 10)  # Top-left red
    assert len(changed_signals) >= 1
    assert controller.currentHex == "#FF0000"
    assert controller.r == 255
    assert controller.g == 0
    assert controller.b == 0
    assert controller.coordX == 10
    assert controller.coordY == 10

    # 3. Select Color directly
    controller.selectColor("#00FF00")
    assert controller.currentHex == "#00FF00"
    assert controller.g == 255

    # 4. Clipboard operations
    controller.copyHex()
    clipboard = QGuiApplication.clipboard()
    if clipboard:
        assert clipboard.text() == "#00FF00"

    controller.copyRgb()
    if clipboard:
        assert clipboard.text() == "rgb(0, 255, 0)"

    controller.copyPaletteCss()
    if clipboard:
        assert ":root {" in clipboard.text()
        assert "--color-palette-1:" in clipboard.text()


def test_color_picker_qml_app_integration(sample_image_path: str):
    """Verify DevImageApp integration with ColorPicker QML views and controller."""
    from PySide6.QtCore import QObject

    from devimage.app.application import DevImageApp

    app = DevImageApp([])
    assert app.load_qml() is True

    root = app.engine.rootObjects()[0]
    app_shell = root.findChild(QObject, "appShell")
    assert app_shell is not None

    # Navigate to color_picker
    app_shell.navigateToTool("color_picker", "Color Picker")
    QGuiApplication.processEvents()

    assert app_shell.property("currentRoute") == "tool"
    assert app_shell.property("activeToolId") == "color_picker"

    # Load image through backend
    app.backend.openImageFile(sample_image_path)
    QGuiApplication.processEvents()

    controller = app.backend.colorPickerController
    assert controller is not None
    assert controller.hasImage is True
    assert len(controller.paletteColors) >= 4

    for obj in app.engine.rootObjects():
        obj.deleteLater()
    QGuiApplication.processEvents()
