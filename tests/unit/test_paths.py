"""Unit tests for path resolution and directory management."""

from pathlib import Path

from devimage.app.paths import (
    get_app_dir,
    get_cache_dir,
    get_config_dir,
    get_logs_dir,
    get_models_dir,
)


def test_paths_are_paths_and_exist():
    """Verify that all path getters return Path instances and directories exist."""
    dirs = [
        get_app_dir(),
        get_config_dir(),
        get_cache_dir(),
        get_logs_dir(),
        get_models_dir(),
    ]

    for d in dirs:
        assert isinstance(d, Path)
        assert d.exists()
        assert d.is_dir()


def test_logs_dir_is_within_app_dir():
    """Verify logs directory is a subdirectory of the app directory."""
    logs_dir = get_logs_dir()
    app_dir = get_app_dir()
    assert str(logs_dir).startswith(str(app_dir))
