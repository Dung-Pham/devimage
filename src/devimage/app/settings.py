"""Persistent settings management for DevImage.

Handles loading, validating, updating, and saving user configuration to disk,
and integrates with Qt Quick through QObject properties and signals.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from PySide6.QtCore import QObject, Signal, Slot

from devimage.app.logging import get_logger
from devimage.app.paths import get_config_dir

logger = get_logger("settings")


class AppConfig(BaseModel):
    """Schema for persistent application settings."""

    theme: str = Field(default="dark", description="UI theme: dark, light, system")
    output_dir: str = Field(default="", description="Default output directory. Empty for same as source.")
    overwrite_mode: str = Field(default="rename", description="Conflict mode: rename, overwrite, ask")
    auto_preview: bool = Field(default=True, description="Automatically generate previews on load")
    default_quality: int = Field(default=85, ge=1, le=100, description="Default JPEG/WebP compression quality")
    window_width: int = Field(default=1100, ge=600, description="Main window width")
    window_height: int = Field(default=720, ge=400, description="Main window height")
    recent_files: list[str] = Field(default_factory=list, description="Recently opened file paths")
    recent_tool: str = Field(default="", description="Last active tool ID")


class SettingsManager(QObject):
    """QObject wrapper managing application settings lifecycle and QML integration."""

    # Qt Signals
    settingsChanged = Signal(str, object)
    themeChanged = Signal(str)

    def __init__(self, config_file: Path | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._config_file = config_file or (get_config_dir() / "settings.json")
        self._config = AppConfig()
        self.load()

    @property
    def config(self) -> AppConfig:
        """Return the active validated AppConfig instance."""
        return self._config

    @Slot(result="QVariantMap")
    def getAll(self) -> dict[str, Any]:
        """Return all settings as a dictionary for QML."""
        return self._config.model_dump()

    @Slot(str, "QVariant", result="QVariant")
    @Slot(str, result="QVariant")
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a specific setting value with optional fallback."""
        val = getattr(self._config, key, default)
        return default if val is None else val

    @Slot(str, "QVariant")
    def set(self, key: str, value: Any) -> None:
        """Set a setting value, emit change signals, and persist."""
        if not hasattr(self._config, key):
            logger.warning("Attempted to set unknown setting key: %s", key)
            return

        current_val = getattr(self._config, key)
        if current_val == value:
            return

        setattr(self._config, key, value)
        logger.debug("Setting updated: %s = %s", key, value)
        self.settingsChanged.emit(key, value)

        if key == "theme":
            self.themeChanged.emit(str(value))

        self.save()

    @Slot(str)
    def addRecentFile(self, file_path: str) -> None:
        """Add a file to the recent files list (maintains max 10 entries)."""
        recent = [f for f in self._config.recent_files if f != file_path]
        recent.insert(0, file_path)
        self._config.recent_files = recent[:10]
        self.settingsChanged.emit("recent_files", self._config.recent_files)
        self.save()

    def load(self) -> None:
        """Load settings from JSON file. Fallback to defaults if file missing or corrupt."""
        if not self._config_file.exists():
            logger.info("Settings file not found. Creating with defaults: %s", self._config_file)
            self.save()
            return

        try:
            with open(self._config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._config = AppConfig(**data)
            logger.info("Loaded settings from %s", self._config_file)
        except Exception as e:
            logger.error("Failed to load settings file (%s). Reverting to defaults.", e)
            self._config = AppConfig()
            self.save()

    def save(self) -> None:
        """Persist current settings to JSON file atomically."""
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            temp_file = self._config_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._config.model_dump(), f, indent=2)
            temp_file.replace(self._config_file)
            logger.debug("Settings saved to %s", self._config_file)
        except Exception as e:
            logger.error("Failed to save settings: %s", e)

    @Slot()
    def resetToDefaults(self) -> None:
        """Reset all configuration values to defaults."""
        self._config = AppConfig()
        self.save()
        for field in AppConfig.model_fields:
            self.settingsChanged.emit(field, getattr(self._config, field))
        self.themeChanged.emit(self._config.theme)
        logger.info("Settings reset to defaults.")
