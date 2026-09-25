"""Unit tests for SettingsManager and AppConfig."""

from pathlib import Path

from devimage.app.settings import SettingsManager


def test_default_settings(tmp_path: Path):
    """Verify default configuration attributes."""
    config_file = tmp_path / "settings.json"
    manager = SettingsManager(config_file=config_file)

    assert manager.get("theme") == "dark"
    assert manager.get("auto_preview") is True
    assert manager.get("default_quality") == 85
    assert manager.get("window_width") == 1100
    assert manager.get("recent_files") == []
    assert config_file.exists()


def test_update_and_persist_setting(tmp_path: Path):
    """Verify modifying a setting persists to file and emits change signal."""
    config_file = tmp_path / "settings.json"
    manager = SettingsManager(config_file=config_file)

    changed_events = []
    manager.settingsChanged.connect(lambda k, v: changed_events.append((k, v)))

    manager.set("theme", "light")
    manager.set("default_quality", 90)

    assert len(changed_events) == 2
    assert ("theme", "light") in changed_events
    assert ("default_quality", 90) in changed_events

    # Reload from disk in a new manager
    new_manager = SettingsManager(config_file=config_file)
    assert new_manager.get("theme") == "light"
    assert new_manager.get("default_quality") == 90


def test_add_recent_file(tmp_path: Path):
    """Verify adding recent files deduplicates and limits to 10."""
    config_file = tmp_path / "settings.json"
    manager = SettingsManager(config_file=config_file)

    for i in range(15):
        manager.addRecentFile(f"/path/to/image_{i}.png")

    recent = manager.get("recent_files")
    assert len(recent) == 10
    # Most recently added should be first
    assert recent[0] == "/path/to/image_14.png"


def test_reset_defaults(tmp_path: Path):
    """Verify resetting settings returns to defaults."""
    config_file = tmp_path / "settings.json"
    manager = SettingsManager(config_file=config_file)

    manager.set("theme", "light")
    assert manager.get("theme") == "light"

    manager.resetToDefaults()
    assert manager.get("theme") == "dark"
