"""DevImage path resolution and directory management.

Provides centralized cross-platform paths for configuration, logs, cache,
and downloaded local AI models.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_APP_NAME = "devimage"


def get_app_dir() -> Path:
    """Return the base user application data directory."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA")
        if base:
            path = Path(base) / _APP_NAME
        else:
            path = Path.home() / f".{_APP_NAME}"
    elif sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / _APP_NAME
    else:
        path = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / _APP_NAME

    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_dir() -> Path:
    """Return the configuration directory."""
    if sys.platform == "win32":
        path = get_app_dir()
    else:
        path = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / _APP_NAME

    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cache_dir() -> Path:
    """Return the cache directory for temporary image files and previews."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            path = Path(base) / _APP_NAME / "cache"
        else:
            path = get_app_dir() / "cache"
    elif sys.platform == "darwin":
        path = Path.home() / "Library" / "Caches" / _APP_NAME
    else:
        path = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / _APP_NAME

    path.mkdir(parents=True, exist_ok=True)
    return path


def get_logs_dir() -> Path:
    """Return the logging directory."""
    path = get_app_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_models_dir() -> Path:
    """Return directory for local AI models (e.g. rembg, onnx)."""
    path = get_app_dir() / "models"
    path.mkdir(parents=True, exist_ok=True)
    return path
