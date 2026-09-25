"""PySide6 controller bridging the Convert Service to QML presentation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from devimage.app.logging import get_logger
from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge
from devimage.engine.image.metadata import extract_metadata
from devimage.tools.convert.service import (
    ConvertOptions,
    ConvertResult,
    ConvertService,
)
from devimage.workers.image_worker import ImageWorker
from devimage.workers.pool import submit_worker

logger = get_logger("tools.convert.controller")


class ConvertController(QObject):
    """QObject controller managing parameters, format choices, and async conversion."""

    imageChanged = Signal()
    optionsChanged = Signal()
    processingStateChanged = Signal()
    progressChanged = Signal()
    resultChanged = Signal()

    convertFinished = Signal(str, str)  # taskId, outputPath
    convertFailed = Signal(str, str)  # taskId, errorMessage

    def __init__(
        self,
        service: ConvertService | None = None,
        signals: AppSignalBridge | None = None,
        settings: SettingsManager | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service or ConvertService()
        self._signals = signals
        self._settings = settings

        # Image state
        self._current_file_path: str = ""
        self._original_format: str = ""

        # Options state
        self._target_format: str = "webp"  # "webp", "png", "jpeg"
        self._quality: int = 90
        self._strip_metadata: bool = False

        # Processing state
        self._is_processing: bool = False
        self._progress: float = 0.0
        self._status_message: str = ""
        self._last_output_path: str = ""
        self._current_worker: ImageWorker | None = None

    # --- Properties ---

    @Property(str, notify=imageChanged)
    def currentFilePath(self) -> str:
        return self._current_file_path

    @Property(bool, notify=imageChanged)
    def hasImage(self) -> bool:
        return bool(self._current_file_path and self._original_format)

    @Property(str, notify=imageChanged)
    def originalFormat(self) -> str:
        return self._original_format

    @Property(str, notify=optionsChanged)
    def targetFormat(self) -> str:
        return self._target_format

    @Property(int, notify=optionsChanged)
    def quality(self) -> int:
        return self._quality

    @Property(bool, notify=optionsChanged)
    def stripMetadata(self) -> bool:
        return self._strip_metadata

    @Property(str, notify=optionsChanged)
    def outputFilename(self) -> str:
        if not self._current_file_path:
            return ""
        dest = self._service.get_default_output_path(
            self._current_file_path, target_format=self._target_format
        )
        return dest.name

    @Property(bool, notify=processingStateChanged)
    def isProcessing(self) -> bool:
        return self._is_processing

    @Property(float, notify=progressChanged)
    def progress(self) -> float:
        return self._progress

    @Property(str, notify=progressChanged)
    def statusMessage(self) -> str:
        return self._status_message

    @Property(str, notify=resultChanged)
    def lastOutputPath(self) -> str:
        return self._last_output_path

    # --- Slots ---

    @Slot(str)
    def loadImage(self, file_path: str) -> None:
        """Load image file, extract format, and notify presentation layer."""
        clean_path = file_path
        if clean_path.startswith("file:///"):
            clean_path = clean_path[8:]
        elif clean_path.startswith("file:"):
            clean_path = clean_path[5:]

        p = Path(clean_path).resolve()
        if not p.is_file():
            logger.warning("ConvertController cannot load missing file: %s", clean_path)
            return

        try:
            meta = extract_metadata(p)
            self._current_file_path = str(p)
            self._original_format = meta.format
            self._last_output_path = ""
            self._progress = 0.0
            self._status_message = "Ready"

            # Auto-suggest best modern format different from source
            if meta.format.upper() in ("PNG", "BMP", "TIFF"):
                self._target_format = "webp"
            elif meta.format.upper() in ("JPEG", "JPG"):
                self._target_format = "webp"
            else:
                self._target_format = "png"

            logger.info("Loaded image for convert: %s (%s)", p.name, meta.format)
            self.imageChanged.emit()
            self.optionsChanged.emit()
            self.resultChanged.emit()
        except Exception as err:
            logger.error("Failed to inspect file format for %s: %s", p, err)
            if self._signals:
                self._signals.triggerError(
                    "Cannot Load Image",
                    f"Could not read metadata for '{p.name}'.",
                    str(err),
                    "Select a valid image file.",
                )

    @Slot(str)
    def setTargetFormat(self, fmt: str) -> None:
        """Update destination format ('webp', 'png', 'jpeg')."""
        norm = fmt.lower()
        if norm not in ("webp", "png", "jpeg") or self._target_format == norm:
            return
        self._target_format = norm
        self.optionsChanged.emit()

    @Slot(int)
    def setQuality(self, val: int) -> None:
        """Update conversion quality (1-100)."""
        clamped = max(1, min(100, val))
        if self._quality == clamped:
            return
        self._quality = clamped
        self.optionsChanged.emit()

    @Slot(bool)
    def setStripMetadata(self, val: bool) -> None:
        """Toggle metadata removal."""
        if self._strip_metadata == val:
            return
        self._strip_metadata = val
        self.optionsChanged.emit()

    @Slot(result=str)
    def executeConvert(self, output_dir: str = "") -> str:
        """Dispatch async conversion to background thread pool."""
        if not self._current_file_path or not self._original_format:
            if self._signals:
                self._signals.triggerError(
                    "No Image Selected",
                    "Please select or drop an image before executing conversion.",
                    "No image file is currently loaded in the workspace.",
                    "Choose an image using the file picker or drag and drop.",
                )
            return ""

        if self._is_processing:
            logger.warning("Conversion operation already in progress.")
            return ""

        opts = ConvertOptions(
            target_format=self._target_format,
            quality=self._quality,
            strip_metadata=self._strip_metadata,
        )

        dest_path = None
        if output_dir:
            dest_path = str(
                self._service.get_default_output_path(
                    self._current_file_path,
                    target_format=self._target_format,
                    output_dir=output_dir,
                )
            )

        self._is_processing = True
        self._progress = 0.0
        self._status_message = "Starting conversion..."
        self.processingStateChanged.emit()
        self.progressChanged.emit()

        if self._signals:
            self._signals.taskProgress.emit("task-convert", 0.0, "Starting conversion...")

        def run_convert(progress_callback: Any = None) -> ConvertResult:
            return self._service.execute(
                input_path=self._current_file_path,
                output_path=dest_path,
                options=opts,
                progress_callback=progress_callback,
            )

        worker = ImageWorker(run_convert, task_id="task-convert")
        self._current_worker = worker

        worker.signals.progress.connect(self._on_progress)
        worker.signals.finished.connect(self._on_finished)
        worker.signals.error.connect(self._on_error)
        worker.signals.cancelled.connect(self._on_cancelled)

        submit_worker(worker)
        return worker.task_id

    @Slot()
    def cancel(self) -> None:
        """Cancel running background conversion."""
        if self._current_worker:
            self._current_worker.cancel()

    # --- Private Handlers ---

    def _on_progress(self, task_id: str, progress: float, message: str) -> None:
        self._progress = progress
        self._status_message = message
        self.progressChanged.emit()
        if self._signals:
            self._signals.taskProgress.emit(task_id, progress, message)

    def _on_finished(self, task_id: str, result: Any) -> None:
        self._is_processing = False
        self._current_worker = None
        if isinstance(result, ConvertResult):
            self._last_output_path = result.output_path
            self._status_message = f"Converted to {result.target_format}"
            self.resultChanged.emit()
            self.processingStateChanged.emit()
            self.convertFinished.emit(task_id, result.output_path)

            if self._signals:
                self._signals.taskCompleted.emit(task_id, result.output_path)
                self._signals.showToast(
                    "success",
                    "Conversion Complete",
                    f"Saved {Path(result.output_path).name}",
                    3000,
                )

    def _on_error(self, task_id: str, error_name: str, error_message: str) -> None:
        self._is_processing = False
        self._current_worker = None
        self._status_message = f"Failed: {error_message}"
        self.processingStateChanged.emit()
        self.convertFailed.emit(task_id, error_message)

        if self._signals:
            self._signals.taskFailed.emit(task_id, error_message)
            self._signals.triggerError(
                "Conversion Operation Failed",
                error_message,
                f"Exception: {error_name}",
                "Please verify the image format and permissions, then try again.",
            )

    def _on_cancelled(self, task_id: str) -> None:
        self._is_processing = False
        self._current_worker = None
        self._status_message = "Cancelled"
        self.processingStateChanged.emit()
        if self._signals:
            self._signals.showToast(
                "info", "Conversion Cancelled", "Operation was cancelled.", 2000
            )
