"""PySide6 QObject controller bridge for Copy Path tool."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication

from devimage.app.logging import get_logger
from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge
from devimage.tools.copy_path.service import PathService

logger = get_logger("tools.copy_path.controller")


class CopyPathController(QObject):
    """QObject bridge between Python PathService and QML CopyPathTool interface."""

    pathChanged = Signal()
    copied = Signal(str)

    def __init__(
        self,
        service: PathService | None = None,
        signals: AppSignalBridge | None = None,
        settings: SettingsManager | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service or PathService()
        self._signals = signals
        self._settings = settings

        self._current_path: str = ""
        self._bundle: dict[str, Any] = self._service.get_path_bundle("")

    # ---------------------------------------------------------
    # Properties for QML
    # ---------------------------------------------------------

    @Property(bool, notify=pathChanged)
    def hasImage(self) -> bool:
        """Whether a valid image is loaded."""
        return bool(self._current_path and Path(self._current_path).is_file())

    @Property(str, notify=pathChanged)
    def currentImagePath(self) -> str:
        """Absolute file path to current loaded image."""
        return self._current_path

    @Property(str, notify=pathChanged)
    def filename(self) -> str:
        """Name of current file."""
        return self._bundle.get("filename", "")

    @Property(str, notify=pathChanged)
    def windowsPath(self) -> str:
        """Windows backslash path."""
        return self._bundle.get("windows_path", "")

    @Property(str, notify=pathChanged)
    def posixPath(self) -> str:
        """POSIX forward slash path."""
        return self._bundle.get("posix_path", "")

    @Property(str, notify=pathChanged)
    def fileUri(self) -> str:
        """file:// URI string."""
        return self._bundle.get("file_uri", "")

    @Property(str, notify=pathChanged)
    def relativePath(self) -> str:
        """Relative path."""
        return self._bundle.get("relative_path", "")

    @Property(str, notify=pathChanged)
    def htmlSnippet(self) -> str:
        """HTML <img> tag."""
        return self._bundle.get("html_snippet", "")

    @Property(str, notify=pathChanged)
    def markdownSnippet(self) -> str:
        """Markdown image snippet."""
        return self._bundle.get("markdown_snippet", "")

    @Property(str, notify=pathChanged)
    def cssSnippet(self) -> str:
        """CSS url() snippet."""
        return self._bundle.get("css_snippet", "")

    @Property(str, notify=pathChanged)
    def base64Uri(self) -> str:
        """Base64 data URI."""
        return self._bundle.get("base64_uri", "")

    @Property(list, notify=pathChanged)
    def snippets(self) -> list[dict[str, Any]]:
        """List of all snippet cards formatted for QML."""
        return self._bundle.get("snippets", [])

    # ---------------------------------------------------------
    # Public Slots for QML
    # ---------------------------------------------------------

    @Slot(str)
    def loadImage(self, file_path: str) -> None:
        """Load and analyze path formats for a given image file."""
        clean_path = self._clean_path(file_path)
        if clean_path == self._current_path:
            return

        self._current_path = clean_path
        self._bundle = self._service.get_path_bundle(clean_path)
        self.pathChanged.emit()

    @Slot(str, str)
    def copyToClipboard(self, text: str, label: str = "Path") -> None:
        """Copy arbitrary text to clipboard and show feedback toast."""
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(text)
            self.copied.emit(label)
            if self._signals:
                preview = (text[:40] + "...") if len(text) > 40 else text
                self._signals.showToast(
                    "success",
                    f"Copied {label}",
                    preview,
                    2000,
                )

    @Slot(str)
    def copySnippet(self, key: str) -> None:
        """Copy a specific snippet by key."""
        for item in self.snippets:
            if item.get("key") == key:
                self.copyToClipboard(item.get("value", ""), item.get("title", "Snippet"))
                return

    @Slot()
    def revealInExplorer(self) -> None:
        """Reveal the current image in the system file manager."""
        if not self._current_path:
            return

        success = self._service.reveal_in_file_manager(self._current_path)
        if success:
            if self._signals:
                self._signals.showToast(
                    "info",
                    "Explorer Opened",
                    Path(self._current_path).name,
                    2000,
                )
        else:
            if self._signals:
                self._signals.showToast(
                    "error",
                    "Explorer Error",
                    "Could not open file in file manager",
                    3000,
                )

    # ---------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------

    def _clean_path(self, path_str: str) -> str:
        """Convert QUrl or string to local filesystem path."""
        if not path_str:
            return ""
        if path_str.startswith("file:"):
            return QUrl(path_str).toLocalFile()
        return path_str
