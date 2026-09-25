"""Headless acceptance tests for Phase 1 Application Shell, navigation, catalog, and components."""

from pathlib import Path

import pytest
from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication

from devimage.app.application import DevImageApp


@pytest.fixture
def app_instance():
    """Create and initialize a DevImageApp instance with offscreen platform."""
    app = DevImageApp([])
    success = app.load_qml()
    assert success is True
    yield app
    for obj in app.engine.rootObjects():
        obj.deleteLater()
    QGuiApplication.processEvents()


def test_tool_catalog_completeness(app_instance: DevImageApp):
    """Verify all 13 tools across the 3 categories exist in the tool catalog."""
    root = app_instance.engine.rootObjects()[0]
    app_shell = root.findChild(QObject, "appShell")
    assert app_shell is not None

    home_view = app_shell.findChild(QObject, "homeView")
    assert home_view is not None

    # Find all ToolCards embedded in Home view
    tool_cards = home_view.findChildren(QObject, "toolCard")
    assert len(tool_cards) == 13, f"Expected 13 tool cards in Home catalog, found {len(tool_cards)}"

    expected_tools = {
        # Image Tools (5)
        "remove_background": False,
        "resize": False,
        "compress": False,
        "convert": False,
        "crop": False,
        # Developer Tools (5)
        "inspector": False,
        "color_picker": False,
        "ocr": False,
        "rename": False,
        "copy_path": False,
        # AI Tools (3)
        "analyze": True,
        "alt_text": True,
        "ai_command": True,
    }

    found_ids = {}
    for card in tool_cards:
        t_id = card.property("toolId")
        is_ai = card.property("isAi")
        assert t_id in expected_tools, f"Unexpected tool ID: {t_id}"
        assert is_ai == expected_tools[t_id], (
            f"Tool {t_id} AI flag mismatch: expected {expected_tools[t_id]}"
        )
        found_ids[t_id] = card.property("title")

    assert set(found_ids.keys()) == set(expected_tools.keys())


def test_navigation_flow(app_instance: DevImageApp):
    """Verify bidirectional navigation between Home and active Tool view."""
    root = app_instance.engine.rootObjects()[0]
    app_shell = root.findChild(QObject, "appShell")
    assert app_shell is not None

    # 1. Initially on home view
    assert app_shell.property("currentRoute") == "home"
    assert app_shell.property("activeToolId") == ""

    # 2. Navigate to tool
    app_shell.navigateToTool("resize", "Resize Image")
    QGuiApplication.processEvents()

    assert app_shell.property("currentRoute") == "tool"
    assert app_shell.property("activeToolId") == "resize"
    assert app_shell.property("activeToolTitle") == "Resize Image"

    # 3. Navigate back to Home
    app_shell.navigateToHome()
    QGuiApplication.processEvents()

    assert app_shell.property("currentRoute") == "home"
    assert app_shell.property("activeToolId") == ""


def test_backend_signal_navigation(app_instance: DevImageApp):
    """Verify backend signals trigger proper navigation in the AppShell."""
    root = app_instance.engine.rootObjects()[0]
    app_shell = root.findChild(QObject, "appShell")
    assert app_shell is not None

    # Trigger tool selection from backend
    app_instance.signals.selectTool("compress")
    QGuiApplication.processEvents()

    assert app_shell.property("currentRoute") == "tool"
    assert app_shell.property("activeToolId") == "compress"

    # Trigger navigate home from backend
    app_instance.signals.navigate("home")
    QGuiApplication.processEvents()

    assert app_shell.property("currentRoute") == "home"


def test_file_picker_and_drop_validation(app_instance: DevImageApp, tmp_path: Path):
    """Verify URL-to-path conversion, image format validation, and file selection signals."""
    backend = app_instance.backend

    # 1. URL to Path conversion
    test_file = tmp_path / "sample.png"
    test_file.write_bytes(b"\x89PNG\r\n\x1a\n")

    file_url = test_file.as_uri()
    resolved_path = backend.urlToPath(file_url)
    assert Path(resolved_path) == test_file

    # Non-url fallback
    assert backend.urlToPath(str(test_file)) == str(test_file)

    # 2. File validation with actual test files
    valid_jpg = tmp_path / "photo.jpg"
    valid_jpg.write_bytes(b"\xff\xd8\xff\xe0")

    invalid_txt = tmp_path / "document.txt"
    invalid_txt.write_text("plain text")

    assert backend.validateImageFile(str(test_file)) is True
    assert backend.validateImageFile(str(valid_jpg)) is True
    assert backend.validateImageFile(str(invalid_txt)) is False
    assert backend.validateImageFile("non_existent_file.png") is False

    # 3. Open image file via backend
    received_files = []
    received_toasts = []
    backend.signals.fileSelected.connect(lambda p: received_files.append(p))
    backend.signals.notify.connect(lambda t, title, m, d: received_toasts.append((t, title, m, d)))

    backend.openImageFile(str(test_file))
    QGuiApplication.processEvents()

    assert len(received_files) == 1
    assert received_files[0] == str(test_file)

    # Verify toast emitted for opened file
    assert len(received_toasts) >= 1
    assert "Loaded" in received_toasts[-1][1] or "sample.png" in received_toasts[-1][2]

    # Verify added to recent files
    recent = backend.settings.get("recent_files")
    assert str(test_file) in recent


def test_tool_shell_and_preview_interaction(app_instance: DevImageApp, tmp_path: Path):
    """Verify ToolShell receives fileSelected signal and updates preview state."""
    root = app_instance.engine.rootObjects()[0]
    app_shell = root.findChild(QObject, "appShell")
    assert app_shell is not None

    # Navigate to tool
    app_shell.navigateToTool("convert", "Format Converter")
    QGuiApplication.processEvents()

    tool_shell = app_shell.findChild(QObject, "activeToolShell")
    assert tool_shell is not None
    assert tool_shell.property("toolId") == "convert"
    assert tool_shell.property("hasImage") is False

    # Create dummy image and open
    sample_img = tmp_path / "photo.jpg"
    sample_img.write_bytes(b"\xff\xd8\xff\xe0")

    app_instance.backend.openImageFile(str(sample_img))
    QGuiApplication.processEvents()

    assert tool_shell.property("currentImagePath") == str(sample_img)
    assert tool_shell.property("hasImage") is True

    # Test reset view slot / property
    tool_shell.resetView()
    assert tool_shell.property("zoomLevel") == 1.0


def test_settings_dialog_and_persistence(app_instance: DevImageApp):
    """Verify settings modifications persist and update application state."""
    settings = app_instance.settings
    settings.resetToDefaults()

    # Verify defaults
    assert settings.get("theme") == "dark"
    assert settings.get("default_quality") == 85
    assert settings.get("overwrite_mode") == "rename"

    # Modify settings
    settings.set("theme", "light")
    settings.set("default_quality", 92)
    settings.set("overwrite_mode", "overwrite")
    settings.set("auto_preview", False)

    # Verify updated values
    assert settings.get("theme") == "light"
    assert settings.get("default_quality") == 92
    assert settings.get("overwrite_mode") == "overwrite"
    assert settings.get("auto_preview") is False

    # Reset to defaults
    settings.resetToDefaults()
    assert settings.get("theme") == "dark"
    assert settings.get("default_quality") == 85
    assert settings.get("overwrite_mode") == "rename"
    assert settings.get("auto_preview") is True


def test_image_preview_dimensions_and_home_drop(app_instance: DevImageApp, tmp_path: Path):
    """Verify that opening an image from Home route navigates to tool and decodes dimensions."""
    from PIL import Image as PILImage

    root = app_instance.engine.rootObjects()[0]
    app_shell = root.findChild(QObject, "appShell")
    assert app_shell is not None

    # Reset to home route
    app_shell.navigateToHome()
    QGuiApplication.processEvents()
    assert app_shell.property("currentRoute") == "home"

    # Create a real 640x480 test image with PIL
    test_img = tmp_path / "canvas_sample.png"
    pil_img = PILImage.new("RGBA", (640, 480), color=(100, 150, 200, 255))
    pil_img.save(test_img)

    # Open image (simulating drag-and-drop or file picker on home)
    app_instance.backend.openImageFile(str(test_img))
    QGuiApplication.processEvents()

    # Verify auto-transition to tool workspace
    assert app_shell.property("currentRoute") == "tool"

    tool_shell = app_shell.findChild(QObject, "activeToolShell")
    assert tool_shell is not None
    assert tool_shell.property("hasImage") is True

    # Verify previewCanvas received image and decoded actual dimensions
    preview_canvas = tool_shell.findChild(QObject, "previewCanvas")
    assert preview_canvas is not None
    assert preview_canvas.property("originalWidth") == 640
    assert preview_canvas.property("originalHeight") == 480
    assert preview_canvas.property("zoomLevel") > 0.0
