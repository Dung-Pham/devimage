"""Comprehensive end-to-end acceptance tests for Phase 3 Developer Tools.

Validates the full headless pipeline for Image Inspector, Color Picker,
Batch Rename, and Copy Path tools, including controller bridges and QML integration.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image
from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication

from devimage.app.application import DevImageApp
from devimage.core.signals import AppSignalBridge
from devimage.tools.color_picker.controller import ColorPickerController
from devimage.tools.color_picker.service import ColorService
from devimage.tools.copy_path.controller import CopyPathController
from devimage.tools.copy_path.service import PathService
from devimage.tools.inspector.controller import InspectorController
from devimage.tools.inspector.service import InspectorService
from devimage.tools.rename.controller import RenameController
from devimage.tools.rename.service import RenameItem, RenameService


@pytest.fixture
def dev_test_images(tmp_path: Path) -> dict[str, Path]:
    """Generate sample images for developer tools verification."""
    img_dir = tmp_path / "fixtures"
    img_dir.mkdir(parents=True, exist_ok=True)

    # 1. 4-color test grid image for color picker and inspector (400x400)
    grid_path = img_dir / "palette_sample.png"
    img = Image.new("RGBA", (400, 400), color=(255, 255, 255, 255))
    for x in range(400):
        for y in range(400):
            if x < 200 and y < 200:
                img.putpixel((x, y), (255, 0, 0, 255))  # Red top-left
            elif x >= 200 and y < 200:
                img.putpixel((x, y), (0, 255, 0, 255))  # Green top-right
            elif x < 200 and y >= 200:
                img.putpixel((x, y), (0, 0, 255, 255))  # Blue bottom-left
            else:
                img.putpixel((x, y), (255, 255, 0, 255))  # Yellow bottom-right
    img.save(grid_path)

    # 2. Additional files for batch rename
    f1 = img_dir / "pic_alpha.jpg"
    f2 = img_dir / "pic_beta.jpg"
    Image.new("RGB", (100, 200), (50, 50, 50)).save(f1)
    Image.new("RGB", (300, 400), (100, 100, 100)).save(f2)

    return {
        "grid": grid_path,
        "rename1": f1,
        "rename2": f2,
    }


class TestPhase3DeveloperServices:
    """Verifies that all 4 standalone services execute cleanly."""

    def test_inspector_service(self, dev_test_images: dict[str, Path]) -> None:
        """Verify technical metadata and EXIF report generation."""
        service = InspectorService()
        meta = service.inspect(dev_test_images["grid"])

        assert meta["width"] == 400
        assert meta["height"] == 400
        assert meta["color_mode"] == "RGBA"
        assert meta["format"] == "PNG"
        assert "1:1" in meta["aspect_ratio"]

        report = service.to_clipboard_text(meta)
        assert "DevImage Inspector Report" in report
        assert "400 × 400" in report

        json_str = service.to_json(meta)
        assert '"width": 400' in json_str

    def test_color_service(self, dev_test_images: dict[str, Path]) -> None:
        """Verify pixel sampling, conversions, and palette extraction."""
        service = ColorService()
        grid_path = str(dev_test_images["grid"])

        # Sample red quadrant
        red_bundle = service.sample_pixel(grid_path, 50, 50)
        assert red_bundle["hex"] == "#FF0000"
        assert red_bundle["r"] == 255
        assert red_bundle["g"] == 0
        assert red_bundle["b"] == 0
        assert red_bundle["rgb_str"] == "rgb(255, 0, 0)"

        # Sample green quadrant
        green_bundle = service.sample_pixel(grid_path, 350, 50)
        assert green_bundle["hex"] == "#00FF00"

        # Dominant palette extraction
        palette = service.extract_palette(grid_path, max_colors=8)
        assert len(palette) >= 4
        hexes = [c["hex"] for c in palette]
        assert "#FF0000" in hexes
        assert "#00FF00" in hexes
        assert "#0000FF" in hexes

    def test_rename_service(self, dev_test_images: dict[str, Path], tmp_path: Path) -> None:
        """Verify pattern substitution, case transforms, and atomic rollback."""
        service = RenameService()
        f1 = str(dev_test_images["rename1"])
        f2 = str(dev_test_images["rename2"])

        # Preview generation with dimension token
        previews = service.generate_preview(
            file_paths=[f1, f2],
            pattern="asset_{n}_{w}x{h}",
            start_index=1,
            padding=3,
        )
        assert len(previews) == 2
        assert previews[0].status == "ok"
        assert previews[0].target_name == "asset_001_100x200.jpg"
        assert previews[1].status == "ok"
        assert previews[1].target_name == "asset_002_300x400.jpg"

        # Rollback execution verification
        bad_item = RenameItem(
            source_path="nonexistent_source_path_xyz.jpg",
            source_name="xyz.jpg",
            target_name="xyz_new.jpg",
            target_path=str(tmp_path / "xyz_new.jpg"),
            status="ok",
            message="Ready",
        )
        count, errors = service.execute_rename([previews[0], bad_item])
        assert count == 0
        assert len(errors) > 0
        # Source file should still exist!
        assert Path(f1).exists()

    def test_copy_path_service(self, dev_test_images: dict[str, Path]) -> None:
        """Verify developer path formats and code snippet generation."""
        service = PathService()
        p = dev_test_images["grid"]
        bundle = service.get_path_bundle(str(p), base_dir=str(p.parent))

        assert bundle["has_file"] is True
        assert bundle["filename"] == "palette_sample.png"
        assert bundle["posix_path"].endswith("/palette_sample.png")
        assert bundle["file_uri"].startswith("file://")
        assert '<img src="./palette_sample.png"' in bundle["html_snippet"]
        assert 'width="400" height="400"' in bundle["html_snippet"]
        assert "![palette_sample](./palette_sample.png)" == bundle["markdown_snippet"]
        assert "data:image/png;base64," in bundle["base64_uri"]

        # Reveal in file manager mock
        with patch("subprocess.Popen") as mock_popen:
            assert service.reveal_in_file_manager(str(p)) is True
            mock_popen.assert_called_once()


class TestPhase3DeveloperControllers:
    """Verifies that PySide6 QObject controllers handle QML interactions cleanly."""

    def test_inspector_controller(
        self, dev_test_images: dict[str, Path], qapp: pytest.fixture
    ) -> None:
        """Verify InspectorController state management and copy slots."""
        signals = AppSignalBridge()
        controller = InspectorController(signals=signals)

        controller.loadImage(str(dev_test_images["grid"]))
        assert controller.hasData is True
        assert controller.dimensions == "400 × 400"
        assert controller.fileName == "palette_sample.png"
        assert controller.colorMode == "RGBA"

        controller.copyAll()
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            assert "DevImage Inspector Report" in clipboard.text()

        controller.copyJson()
        if clipboard:
            assert '"width": 400' in clipboard.text()

    def test_color_picker_controller(
        self, dev_test_images: dict[str, Path], qapp: pytest.fixture
    ) -> None:
        """Verify ColorPickerController pixel sampling and color selection."""
        signals = AppSignalBridge()
        controller = ColorPickerController(signals=signals)

        controller.loadImage(str(dev_test_images["grid"]))
        assert controller.hasImage is True

        controller.sampleAt(50, 50)
        assert controller.currentHex == "#FF0000"

        controller.selectColor("#0000FF")
        assert controller.currentHex == "#0000FF"

        controller.copyHex()
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            assert clipboard.text() == "#0000FF"

    def test_rename_controller(self, dev_test_images: dict[str, Path], tmp_path: Path) -> None:
        """Verify RenameController batch queuing and execution."""
        signals = AppSignalBridge()
        controller = RenameController(signals=signals)

        f1 = tmp_path / "batch_one.png"
        f2 = tmp_path / "batch_two.png"
        f1.write_text("1")
        f2.write_text("2")

        controller.addFiles([str(f1), str(f2)])
        assert controller.fileCount == 2
        assert controller.hasFiles is True

        controller.applyPreset("numbered")
        assert controller.pattern == "{name}_{n}"

        count = controller.executeBatchRename()
        assert count == 2
        assert (tmp_path / "batch_one_001.png").exists()
        assert (tmp_path / "batch_two_002.png").exists()

    def test_copy_path_controller(
        self, dev_test_images: dict[str, Path], qapp: pytest.fixture
    ) -> None:
        """Verify CopyPathController snippet copying."""
        signals = AppSignalBridge()
        controller = CopyPathController(signals=signals)

        controller.loadImage(str(dev_test_images["grid"]))
        assert controller.hasImage is True

        controller.copySnippet("posix")
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            assert clipboard.text() == controller.posixPath


class TestPhase3AppShellIntegration:
    """Verifies that all Phase 3 tools are exposed to QML and navigate cleanly in AppShell."""

    def test_app_shell_exposes_all_phase3_controllers(self) -> None:
        """Verify DevImageApp exposes all developer tool controllers to root context."""
        app = DevImageApp([])
        assert app.inspector_controller is not None
        assert app.color_controller is not None
        assert app.rename_controller is not None
        assert app.copy_path_controller is not None
        assert app.load_qml() is True

    def test_full_navigation_across_all_phase3_tools(self) -> None:
        """Verify AppShell navigation between all 4 developer tools."""
        app = DevImageApp([])
        assert app.load_qml() is True

        root_objects = app.engine.rootObjects()
        assert len(root_objects) > 0
        main_window = root_objects[0]
        app_shell = main_window.findChild(QObject, "appShell")
        assert app_shell is not None

        # Navigate to Inspector
        app_shell.setProperty("currentView", "tool")
        app_shell.setProperty("activeToolId", "inspector")
        assert app_shell.property("activeToolId") == "inspector"

        # Navigate to Color Picker
        app_shell.setProperty("activeToolId", "color_picker")
        assert app_shell.property("activeToolId") == "color_picker"

        # Navigate to Batch Rename
        app_shell.setProperty("activeToolId", "rename")
        assert app_shell.property("activeToolId") == "rename"

        # Navigate to Copy Path
        app_shell.setProperty("activeToolId", "copy_path")
        assert app_shell.property("activeToolId") == "copy_path"
