"""Unit tests for Copy Path service, controller bridge, and QML integration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent

from devimage.app.application import DevImageApp
from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge
from devimage.tools.copy_path.controller import CopyPathController
from devimage.tools.copy_path.service import PathService


@pytest.fixture
def sample_test_image(tmp_path: Path) -> Path:
    """Create a sample PNG image."""
    img_path = tmp_path / "hero_banner.png"
    img = Image.new("RGBA", (300, 200), color=(100, 150, 200, 255))
    img.save(img_path)
    return img_path


def test_path_service_formatting(sample_test_image: Path) -> None:
    """Test PathService formatting methods."""
    service = PathService()
    img_str = str(sample_test_image)

    # 1. MIME types
    assert service.get_mime_type(".png") == "image/png"
    assert service.get_mime_type(".jpg") == "image/jpeg"
    assert service.get_mime_type(".webp") == "image/webp"

    # 2. Path variations
    bundle = service.get_path_bundle(img_str, base_dir=str(sample_test_image.parent))
    assert bundle["has_file"] is True
    assert bundle["filename"] == "hero_banner.png"
    assert bundle["stem"] == "hero_banner"
    assert bundle["ext"] == ".png"
    assert bundle["width"] == 300
    assert bundle["height"] == 200

    assert "hero_banner.png" in bundle["windows_path"]
    assert "hero_banner.png" in bundle["posix_path"]
    assert "/" in bundle["posix_path"]
    assert bundle["file_uri"].startswith("file://")
    assert "hero_banner.png" in bundle["file_uri"]

    # 3. Snippets
    assert '<img src="./hero_banner.png"' in bundle["html_snippet"]
    assert 'width="300" height="200"' in bundle["html_snippet"]
    assert "![hero_banner](./hero_banner.png)" == bundle["markdown_snippet"]
    assert "background-image: url('./hero_banner.png');" == bundle["css_snippet"]
    assert "data:image/png;base64," in bundle["base64_uri"]

    # 4. Snippet card list
    keys = [item["key"] for item in bundle["snippets"]]
    assert "windows" in keys
    assert "posix" in keys
    assert "uri" in keys
    assert "html" in keys
    assert "markdown" in keys
    assert "css" in keys
    assert "base64" in keys


def test_path_service_missing_file() -> None:
    """Test PathService with non-existent file."""
    service = PathService()
    bundle = service.get_path_bundle("nonexistent_image_123.png")
    assert bundle["has_file"] is False
    assert bundle["snippets"] == []


def test_path_service_reveal_in_file_manager(sample_test_image: Path) -> None:
    """Test reveal in file manager calls subprocess."""
    service = PathService()
    with patch("subprocess.Popen") as mock_popen:
        assert service.reveal_in_file_manager(str(sample_test_image)) is True
        mock_popen.assert_called_once()

    # Nonexistent path returns False
    assert service.reveal_in_file_manager("missing_file.xyz") is False


def test_copy_path_controller_lifecycle(qapp: pytest.fixture, sample_test_image: Path) -> None:
    """Test CopyPathController properties, slots, and signals."""
    signals = AppSignalBridge()
    settings = SettingsManager()
    controller = CopyPathController(signals=signals, settings=settings)

    assert controller.hasImage is False

    controller.loadImage(str(sample_test_image))
    assert controller.hasImage is True
    assert controller.filename == "hero_banner.png"
    assert "hero_banner.png" in controller.posixPath
    assert controller.htmlSnippet.startswith("<img")
    assert controller.base64Uri.startswith("data:image/png;base64,")
    assert len(controller.snippets) > 5

    # Test copy
    controller.copySnippet("posix")
    clipboard = QGuiApplication.clipboard()
    if clipboard:
        assert clipboard.text() == controller.posixPath

    # Test reveal
    with patch("subprocess.Popen"):
        controller.revealInExplorer()


def test_copy_path_qml_component_instantiation(qapp: pytest.fixture) -> None:
    """Verify CopyPathTool.qml parses and loads cleanly in QML."""
    signals = AppSignalBridge()
    settings = SettingsManager()
    controller = CopyPathController(signals=signals, settings=settings)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", None)
    engine.rootContext().setContextProperty("copyPathController", controller)

    tool_path = (
        Path(__file__).resolve().parent.parent.parent
        / "src"
        / "devimage"
        / "ui"
        / "qml"
        / "tools"
        / "CopyPathTool.qml"
    )
    component = QQmlComponent(engine, str(tool_path))
    assert not component.isError(), f"CopyPathTool.qml errors: {component.errors()}"


def test_copy_path_qml_app_integration() -> None:
    """Verify DevImageApp exposes copyPathController and loads full QML tree."""
    app = DevImageApp([])
    assert app.load_qml() is True
