"""Image Inspector controller bridge exposing metadata and actions to QML."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QGuiApplication

from devimage.app.logging import get_logger
from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge
from devimage.tools.inspector.service import InspectorService

logger = get_logger("tools.inspector.controller")


class InspectorController(QObject):
    """PySide6 controller exposing image inspection data and clipboard export."""

    inspectionChanged = Signal()

    def __init__(
        self,
        service: InspectorService | None = None,
        signals: AppSignalBridge | None = None,
        settings: SettingsManager | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service or InspectorService()
        self._signals = signals
        self._settings = settings

        self._current_path: str = ""
        self._data: dict[str, Any] = {}
        self._json_cache: str = ""
        self._text_cache: str = ""

    # Properties
    @Property(str, notify=inspectionChanged)
    def currentPath(self) -> str:
        return self._current_path

    @Property(bool, notify=inspectionChanged)
    def hasData(self) -> bool:
        return bool(self._data)

    @Property(str, notify=inspectionChanged)
    def fileName(self) -> str:
        return str(self._data.get("file_name", ""))

    @Property(str, notify=inspectionChanged)
    def fileDirectory(self) -> str:
        return str(self._data.get("file_directory", ""))

    @Property(str, notify=inspectionChanged)
    def format(self) -> str:
        return str(self._data.get("format", ""))

    @Property(str, notify=inspectionChanged)
    def fileSize(self) -> str:
        return str(self._data.get("file_size_formatted", ""))

    @Property(str, notify=inspectionChanged)
    def dimensions(self) -> str:
        return str(self._data.get("dimensions", ""))

    @Property(str, notify=inspectionChanged)
    def aspectRatio(self) -> str:
        return str(self._data.get("aspect_ratio", ""))

    @Property(str, notify=inspectionChanged)
    def colorMode(self) -> str:
        return str(self._data.get("color_mode", ""))

    @Property(bool, notify=inspectionChanged)
    def hasAlpha(self) -> bool:
        return bool(self._data.get("has_alpha", False))

    @Property(str, notify=inspectionChanged)
    def colorSpace(self) -> str:
        return str(self._data.get("color_space", ""))

    @Property(str, notify=inspectionChanged)
    def dpi(self) -> str:
        return str(self._data.get("dpi", ""))

    @Property(bool, notify=inspectionChanged)
    def hasExif(self) -> bool:
        return bool(self._data.get("has_exif", False))

    @Property(int, notify=inspectionChanged)
    def exifCount(self) -> int:
        return int(self._data.get("exif_count", 0))

    @Property("QVariantList", notify=inspectionChanged)
    def exifList(self) -> list[dict[str, str]]:
        tags = self._data.get("exif_tags", {})
        return [{"key": k, "value": str(v)} for k, v in sorted(tags.items())]

    @Property("QStringList", notify=inspectionChanged)
    def optimizationTips(self) -> list[str]:
        return list(self._data.get("optimization_tips", []))

    @Property(str, notify=inspectionChanged)
    def jsonSummary(self) -> str:
        return self._json_cache

    @Slot(str)
    def loadImage(self, file_path: str) -> None:
        """Inspect and load metadata for image at file_path."""
        if not file_path:
            self._current_path = ""
            self._data = {}
            self._json_cache = ""
            self._text_cache = ""
            self.inspectionChanged.emit()
            return

        clean_path = file_path
        if clean_path.startswith("file:"):
            clean_path = QUrl(clean_path).toLocalFile()

        try:
            self._data = self._service.inspect(clean_path)
            self._current_path = clean_path
            self._json_cache = self._service.to_json(self._data)
            self._text_cache = self._service.to_clipboard_text(self._data)
            logger.info(
                "Inspected %s (%s)", self._data.get("file_name"), self._data.get("dimensions")
            )
            self.inspectionChanged.emit()
        except Exception as err:
            logger.error("Failed to inspect %s: %s", clean_path, err)
            if self._signals:
                self._signals.triggerError(
                    "Inspection Failed",
                    f"Unable to inspect image metadata for {clean_path}",
                    str(err),
                    "Verify the file is a valid, readable image.",
                )

    @Slot()
    def copyAll(self) -> None:
        """Copy formatted human-readable report to system clipboard."""
        if not self._text_cache:
            return
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(self._text_cache)
            if self._signals:
                self._signals.showToast(
                    "success", "Copied", "Full inspection report copied to clipboard", 2500
                )

    @Slot()
    def copyJson(self) -> None:
        """Copy JSON representation to system clipboard."""
        if not self._json_cache:
            return
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(self._json_cache)
            if self._signals:
                self._signals.showToast(
                    "success", "Copied", "JSON metadata copied to clipboard", 2500
                )

    @Slot()
    def openContainingFolder(self) -> None:
        """Open the directory containing the current image in Windows Explorer."""
        dir_path = self.fileDirectory
        if dir_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir_path))
