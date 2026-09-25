"""PySide6 QObject controller bridge for Batch Rename tool."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from devimage.app.logging import get_logger
from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge
from devimage.tools.rename.service import RenameItem, RenameService

logger = get_logger("tools.rename.controller")


class RenameController(QObject):
    """QObject bridge between Python RenameService and QML RenameTool interface."""

    patternChanged = Signal()
    startIndexChanged = Signal()
    paddingChanged = Signal()
    caseTransformChanged = Signal()
    findReplaceChanged = Signal()
    filesChanged = Signal()
    previewsChanged = Signal()
    isProcessingChanged = Signal()
    renamed = Signal(int)
    errorOccurred = Signal(str)

    def __init__(
        self,
        service: RenameService | None = None,
        signals: AppSignalBridge | None = None,
        settings: SettingsManager | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service or RenameService()
        self._signals = signals
        self._settings = settings

        self._files: list[str] = []
        self._pattern: str = "{name}_{n}"
        self._start_index: int = 1
        self._padding: int = 3
        self._case_transform: str = "none"
        self._find_text: str = ""
        self._replace_text: str = ""
        self._is_processing: bool = False
        self._status_message: str = "Ready"

        self._preview_items: list[RenameItem] = []
        self._preview_dicts: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # Properties for QML
    # ---------------------------------------------------------

    @Property(str, notify=patternChanged)
    def pattern(self) -> str:
        """Template naming pattern."""
        return self._pattern

    @pattern.setter
    def pattern(self, val: str) -> None:
        if self._pattern != val:
            self._pattern = val
            self.patternChanged.emit()
            self._update_previews()

    @Property(int, notify=startIndexChanged)
    def startIndex(self) -> int:
        """Start sequence number for indexing."""
        return self._start_index

    @startIndex.setter
    def startIndex(self, val: int) -> None:
        val = max(0, val)
        if self._start_index != val:
            self._start_index = val
            self.startIndexChanged.emit()
            self._update_previews()

    @Property(int, notify=paddingChanged)
    def padding(self) -> int:
        """Zero-padding length (e.g. 3 -> 001)."""
        return self._padding

    @padding.setter
    def padding(self, val: int) -> None:
        val = max(1, min(10, val))
        if self._padding != val:
            self._padding = val
            self.paddingChanged.emit()
            self._update_previews()

    @Property(str, notify=caseTransformChanged)
    def caseTransform(self) -> str:
        """Case transform mode: none, lowercase, uppercase, kebab-case, snake_case."""
        return self._case_transform

    @caseTransform.setter
    def caseTransform(self, val: str) -> None:
        if self._case_transform != val:
            self._case_transform = val
            self.caseTransformChanged.emit()
            self._update_previews()

    @Property(str, notify=findReplaceChanged)
    def findText(self) -> str:
        """Search text to replace in filenames."""
        return self._find_text

    @findText.setter
    def findText(self, val: str) -> None:
        if self._find_text != val:
            self._find_text = val
            self.findReplaceChanged.emit()
            self._update_previews()

    @Property(str, notify=findReplaceChanged)
    def replaceText(self) -> str:
        """Replacement string."""
        return self._replace_text

    @replaceText.setter
    def replaceText(self, val: str) -> None:
        if self._replace_text != val:
            self._replace_text = val
            self.findReplaceChanged.emit()
            self._update_previews()

    @Property(int, notify=filesChanged)
    def fileCount(self) -> int:
        """Total number of files in the batch queue."""
        return len(self._files)

    @Property(bool, notify=filesChanged)
    def hasFiles(self) -> bool:
        """Whether there are any files queued."""
        return len(self._files) > 0

    @Property(list, notify=previewsChanged)
    def previews(self) -> list[dict[str, Any]]:
        """List of preview items formatted for QML."""
        return self._preview_dicts

    @Property(bool, notify=previewsChanged)
    def hasCollisions(self) -> bool:
        """Whether any items in the preview have collisions or errors."""
        return any(
            item.status in ("collision", "invalid", "exists") for item in self._preview_items
        )

    @Property(int, notify=previewsChanged)
    def readyCount(self) -> int:
        """Number of items valid and ready to rename."""
        return sum(
            1
            for item in self._preview_items
            if item.status == "ok" and item.source_name != item.target_name
        )

    @Property(bool, notify=isProcessingChanged)
    def isProcessing(self) -> bool:
        """Whether batch rename execution is active."""
        return self._is_processing

    @Property(str, notify=previewsChanged)
    def statusMessage(self) -> str:
        """Status overview message."""
        return self._status_message

    # ---------------------------------------------------------
    # Public Slots for QML
    # ---------------------------------------------------------

    @Slot(str)
    def setPattern(self, pattern: str) -> None:
        """Set naming pattern from QML."""
        self.pattern = pattern

    @Slot(int)
    def setStartIndex(self, val: int) -> None:
        """Set start index from QML."""
        self.startIndex = val

    @Slot(int)
    def setPadding(self, val: int) -> None:
        """Set zero-padding from QML."""
        self.padding = val

    @Slot(str)
    def setCaseTransform(self, val: str) -> None:
        """Set case transform mode from QML."""
        self.caseTransform = val

    @Slot(str, str)
    def setFindReplace(self, find_text: str, replace_text: str) -> None:
        """Set find and replace strings."""
        if self._find_text != find_text or self._replace_text != replace_text:
            self._find_text = find_text
            self._replace_text = replace_text
            self.findReplaceChanged.emit()
            self._update_previews()

    @Slot(str)
    def applyPreset(self, preset_name: str) -> None:
        """Apply a named preset pattern."""
        preset = preset_name.lower().strip()
        if preset == "numbered":
            self._pattern = "{name}_{n}"
            self._padding = 3
            self._case_transform = "none"
        elif preset == "date_name":
            self._pattern = "{date}_{name}"
            self._case_transform = "none"
        elif preset == "dimensions":
            self._pattern = "{name}_{w}x{h}"
            self._case_transform = "none"
        elif preset in ("kebab", "kebab-case"):
            self._pattern = "{name}"
            self._case_transform = "kebab-case"
        elif preset in ("snake", "snake_case"):
            self._pattern = "{name}"
            self._case_transform = "snake_case"
        elif preset == "clean_number":
            self._pattern = "img_{n}"
            self._padding = 3
            self._case_transform = "none"

        self.patternChanged.emit()
        self.paddingChanged.emit()
        self.caseTransformChanged.emit()
        self._update_previews()

    @Slot(str)
    def addFile(self, file_path: str) -> None:
        """Add a single file to the batch."""
        clean = self._clean_path(file_path)
        if clean and clean not in self._files and Path(clean).is_file():
            self._files.append(clean)
            self.filesChanged.emit()
            self._update_previews()

    @Slot(list)
    def addFiles(self, file_paths: list[str]) -> None:
        """Add multiple files to the batch."""
        added = False
        for p in file_paths:
            clean = self._clean_path(str(p))
            if clean and clean not in self._files and Path(clean).is_file():
                self._files.append(clean)
                added = True
        if added:
            self.filesChanged.emit()
            self._update_previews()

    @Slot(int)
    def removeFile(self, index: int) -> None:
        """Remove a file at given index from the batch."""
        if 0 <= index < len(self._files):
            self._files.pop(index)
            self.filesChanged.emit()
            self._update_previews()

    @Slot()
    def clearFiles(self) -> None:
        """Clear all files from the batch."""
        if self._files:
            self._files.clear()
            self.filesChanged.emit()
            self._update_previews()

    @Slot(result=int)
    def executeBatchRename(self) -> int:
        """Execute the batch rename operation."""
        if not self._files or not self._preview_items:
            return 0

        if self.hasCollisions:
            err_msg = "Cannot execute rename: resolve name collisions or errors first."
            self.errorOccurred.emit(err_msg)
            if self._signals:
                self._signals.triggerError(
                    "Rename Collision",
                    err_msg,
                    "One or more target filenames conflict with existing files or duplicate each other.",
                    "Adjust the template pattern, start index, or remove conflicting files.",
                )
            return 0

        self._is_processing = True
        self.isProcessingChanged.emit()

        try:
            count, errors = self._service.execute_rename(self._preview_items)
            if errors:
                err_str = "; ".join(errors)
                self.errorOccurred.emit(err_str)
                if self._signals:
                    self._signals.triggerError(
                        "Rename Error",
                        "Batch rename encountered an error and rolled back changes.",
                        err_str,
                        "Verify file permissions and ensure files are not in use by another program.",
                    )
                return 0

            # Update the tracked file list to the new target paths
            new_paths: list[str] = []
            for item in self._preview_items:
                if item.status == "ok" and item.source_name != item.target_name:
                    new_paths.append(item.target_path)
                else:
                    new_paths.append(item.source_path)

            self._files = new_paths
            self.filesChanged.emit()
            self._update_previews()
            self.renamed.emit(count)

            if self._signals:
                self._signals.showToast(
                    "success",
                    "Batch Rename Complete",
                    f"Successfully renamed {count} file(s)",
                    3000,
                )

            return count

        finally:
            self._is_processing = False
            self.isProcessingChanged.emit()

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

    def _update_previews(self) -> None:
        """Recalculate dry-run preview for all queued files."""
        if not self._files:
            self._preview_items = []
            self._preview_dicts = []
            self._status_message = "No files added"
            self.previewsChanged.emit()
            return

        self._preview_items = self._service.generate_preview(
            file_paths=self._files,
            pattern=self._pattern,
            start_index=self._start_index,
            padding=self._padding,
            case_transform=self._case_transform,
            find_text=self._find_text,
            replace_text=self._replace_text,
        )
        self._preview_dicts = [item.to_dict() for item in self._preview_items]

        # Status summary
        collisions = sum(1 for it in self._preview_items if it.status == "collision")
        exists = sum(1 for it in self._preview_items if it.status == "exists")
        invalid = sum(1 for it in self._preview_items if it.status == "invalid")
        ready = sum(
            1
            for it in self._preview_items
            if it.status == "ok" and it.source_name != it.target_name
        )

        if collisions > 0:
            self._status_message = f"Warning: {collisions} duplicate collision(s) detected"
        elif exists > 0:
            self._status_message = f"Warning: {exists} target file(s) already exist on disk"
        elif invalid > 0:
            self._status_message = f"Error: {invalid} invalid target filename(s)"
        elif ready == 0:
            self._status_message = "All filenames are already unchanged"
        else:
            self._status_message = f"Ready to rename {ready} file(s)"

        self.previewsChanged.emit()
