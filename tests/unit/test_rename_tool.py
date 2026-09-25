"""Unit tests for Batch Rename service and controller bridge."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image
from PySide6.QtCore import QCoreApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent

from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge
from devimage.tools.rename.controller import RenameController
from devimage.tools.rename.service import RenameItem, RenameService


@pytest.fixture
def sample_images(tmp_path: Path) -> list[Path]:
    """Create three temporary image files for testing."""
    files: list[Path] = []
    for i in range(1, 4):
        p = tmp_path / f"Photo_{i}.png"
        img = Image.new("RGB", (100 * i, 150 * i), color=(i * 40, i * 40, i * 40))
        img.save(p)
        files.append(p)
    return files


def test_rename_service_build_target_name(sample_images: list[Path]) -> None:
    """Test pattern substitution and token formatting."""
    service = RenameService()
    img_path = str(sample_images[0])  # Photo_1.png (100x150)

    # 1. Basic index and padding
    res = service.build_target_name(
        source_path=img_path,
        index=1,
        pattern="{name}_{n}",
        padding=3,
    )
    assert res == "Photo_1_001.png"

    # 2. Case transform
    res_lower = service.build_target_name(
        source_path=img_path,
        index=1,
        pattern="{name}",
        case_transform="lowercase",
    )
    assert res_lower == "photo_1.png"

    res_kebab = service.build_target_name(
        source_path=img_path,
        index=1,
        pattern="{name}",
        case_transform="kebab-case",
    )
    assert res_kebab == "photo-1.png"

    # 3. Dimensions token
    res_dim = service.build_target_name(
        source_path=img_path,
        index=1,
        pattern="{name}_{w}x{h}",
    )
    assert res_dim == "Photo_1_100x150.png"

    # 4. Find & Replace
    res_fr = service.build_target_name(
        source_path=img_path,
        index=1,
        pattern="{name}",
        find_text="Photo",
        replace_text="Img",
    )
    assert res_fr == "Img_1.png"


def test_rename_service_preview_and_collisions(tmp_path: Path) -> None:
    """Test collision detection and preview statuses."""
    service = RenameService()

    file1 = tmp_path / "img_a.png"
    file2 = tmp_path / "img_b.png"
    file1.touch()
    file2.touch()

    # Case 1: Duplicate target in batch causes collision
    previews = service.generate_preview(
        file_paths=[str(file1), str(file2)],
        pattern="static_target",
    )
    assert len(previews) == 2
    assert previews[0].status == "collision"
    assert previews[1].status == "collision"

    # Case 2: Target already exists on disk
    existing = tmp_path / "already_exists.png"
    existing.touch()

    previews_exist = service.generate_preview(
        file_paths=[str(file1)],
        pattern="already_exists",
    )
    assert previews_exist[0].status == "exists"

    # Case 3: Valid pattern
    previews_valid = service.generate_preview(
        file_paths=[str(file1), str(file2)],
        pattern="asset_{n}",
        start_index=1,
        padding=2,
    )
    assert previews_valid[0].status == "ok"
    assert previews_valid[0].target_name == "asset_01.png"
    assert previews_valid[1].status == "ok"
    assert previews_valid[1].target_name == "asset_02.png"


def test_rename_service_execution_and_rollback(tmp_path: Path) -> None:
    """Test actual filesystem renaming and rollback on error."""
    service = RenameService()

    f1 = tmp_path / "alpha.txt"
    f2 = tmp_path / "beta.txt"
    f1.write_text("alpha")
    f2.write_text("beta")

    items = [
        RenameItem(
            source_path=str(f1),
            source_name="alpha.txt",
            target_name="alpha_renamed.txt",
            target_path=str(tmp_path / "alpha_renamed.txt"),
            status="ok",
            message="Ready",
        ),
        RenameItem(
            source_path=str(f2),
            source_name="beta.txt",
            target_name="beta_renamed.txt",
            target_path=str(tmp_path / "beta_renamed.txt"),
            status="ok",
            message="Ready",
        ),
    ]

    count, errors = service.execute_rename(items)
    assert count == 2
    assert not errors
    assert not f1.exists()
    assert (tmp_path / "alpha_renamed.txt").exists()
    assert (tmp_path / "beta_renamed.txt").exists()

    # Rollback test: simulate failure on nonexistent source
    f3 = tmp_path / "gamma.txt"
    f3.write_text("gamma")

    bad_items = [
        RenameItem(
            source_path=str(f3),
            source_name="gamma.txt",
            target_name="gamma_new.txt",
            target_path=str(tmp_path / "gamma_new.txt"),
            status="ok",
            message="Ready",
        ),
        RenameItem(
            source_path=str(tmp_path / "missing_source.txt"),
            source_name="missing_source.txt",
            target_name="missing_new.txt",
            target_path=str(tmp_path / "missing_new.txt"),
            status="ok",
            message="Ready",
        ),
    ]

    count_fail, errors_fail = service.execute_rename(bad_items)
    assert count_fail == 0
    assert len(errors_fail) > 0
    # gamma.txt must be safely restored to original path!
    assert f3.exists()
    assert not (tmp_path / "gamma_new.txt").exists()


def test_rename_controller_lifecycle(sample_images: list[Path]) -> None:
    """Test RenameController bridge slots, signals, and presets."""
    signals = AppSignalBridge()
    controller = RenameController(signals=signals)

    paths = [str(p) for p in sample_images]
    controller.addFiles(paths)
    assert controller.fileCount == 3
    assert controller.hasFiles is True
    assert len(controller.previews) == 3

    # Test presets
    controller.applyPreset("numbered")
    assert controller.pattern == "{name}_{n}"
    assert controller.padding == 3

    controller.applyPreset("dimensions")
    assert controller.pattern == "{name}_{w}x{h}"

    controller.applyPreset("kebab")
    assert controller.caseTransform == "kebab-case"

    # Remove file
    controller.removeFile(0)
    assert controller.fileCount == 2

    # Clear files
    controller.clearFiles()
    assert controller.fileCount == 0
    assert controller.hasFiles is False


def test_rename_controller_execute(tmp_path: Path) -> None:
    """Test controller execution of batch rename."""
    signals = AppSignalBridge()
    controller = RenameController(signals=signals)

    f1 = tmp_path / "test_one.png"
    f2 = tmp_path / "test_two.png"
    f1.write_text("1")
    f2.write_text("2")

    controller.addFiles([str(f1), str(f2)])
    controller.setPattern("renamed_{n}")
    controller.setStartIndex(10)
    controller.setPadding(2)

    count = controller.executeBatchRename()
    assert count == 2
    assert (tmp_path / "renamed_10.png").exists()
    assert (tmp_path / "renamed_11.png").exists()
    assert not f1.exists()
    assert not f2.exists()


def test_rename_qml_components_instantiation(qtbot: pytest.fixture) -> None:
    """Verify that RenameTool.qml and BatchRenameWorkspace.qml load cleanly in QML engine."""
    app = QCoreApplication.instance()
    if app is None:
        pytest.skip("Qt application instance unavailable")

    signals = AppSignalBridge()
    settings = SettingsManager()
    controller = RenameController(signals=signals, settings=settings)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", None)
    engine.rootContext().setContextProperty("renameController", controller)

    # 1. RenameTool.qml
    rename_tool_path = (
        Path(__file__).resolve().parent.parent.parent
        / "src"
        / "devimage"
        / "ui"
        / "qml"
        / "tools"
        / "RenameTool.qml"
    )
    component1 = QQmlComponent(engine, str(rename_tool_path))
    assert not component1.isError(), f"RenameTool.qml errors: {component1.errors()}"

    # 2. BatchRenameWorkspace.qml
    workspace_path = (
        Path(__file__).resolve().parent.parent.parent
        / "src"
        / "devimage"
        / "ui"
        / "qml"
        / "components"
        / "BatchRenameWorkspace.qml"
    )
    component2 = QQmlComponent(engine, str(workspace_path))
    assert not component2.isError(), f"BatchRenameWorkspace.qml errors: {component2.errors()}"
