"""PySide6 controller bridging the Compress Service to QML presentation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from devimage.app.logging import get_logger
from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge
from devimage.tools.compress.service import (
    CompressOptions,
    CompressResult,
    CompressService,
)
from devimage.workers.image_worker import ImageWorker
from devimage.workers.pool import submit_worker

logger = get_logger("tools.compress.controller")


def format_bytes(size: int) -> str:
    """Format bytes into human-readable string."""
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.2f} MB"


class CompressController(QObject):
    """QObject controller managing parameters, estimation, and async compression."""

    imageChanged = Signal()
    optionsChanged = Signal()
    estimationChanged = Signal()
    processingStateChanged = Signal()
    progressChanged = Signal()
    resultChanged = Signal()

    compressFinished = Signal(str, str)  # taskId, outputPath
    compressFailed = Signal(str, str)  # taskId, errorMessage

    def __init__(
        self,
        service: CompressService | None = None,
        signals: AppSignalBridge | None = None,
        settings: SettingsManager | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service or CompressService()
        self._signals = signals
        self._settings = settings

        # Image state
        self._current_file_path: str = ""
        self._original_size_bytes: int = 0

        # Options state
        default_q = self._settings.get("default_quality", 80) if self._settings else 80
        self._quality: int = default_q
        self._target_format: str = "original"  # "original", "webp", "jpeg"
        self._strip_metadata: bool = True
        self._png_quantize: bool = False

        # Estimation state
        self._estimated_size_bytes: int = 0
        self._estimated_reduction: float = 0.0

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
        return bool(self._current_file_path and self._original_size_bytes > 0)

    @Property(int, notify=imageChanged)
    def originalSizeBytes(self) -> int:
        return self._original_size_bytes

    @Property(str, notify=imageChanged)
    def originalSizeText(self) -> str:
        return format_bytes(self._original_size_bytes) if self._original_size_bytes > 0 else "—"

    @Property(int, notify=optionsChanged)
    def quality(self) -> int:
        return self._quality

    @Property(str, notify=optionsChanged)
    def targetFormat(self) -> str:
        return self._target_format

    @Property(bool, notify=optionsChanged)
    def stripMetadata(self) -> bool:
        return self._strip_metadata

    @Property(bool, notify=optionsChanged)
    def pngQuantize(self) -> bool:
        return self._png_quantize

    @Property(int, notify=estimationChanged)
    def estimatedSizeBytes(self) -> int:
        return self._estimated_size_bytes

    @Property(str, notify=estimationChanged)
    def estimatedSizeText(self) -> str:
        return format_bytes(self._estimated_size_bytes) if self._estimated_size_bytes > 0 else "—"

    @Property(float, notify=estimationChanged)
    def estimatedReduction(self) -> float:
        return self._estimated_reduction

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
        """Load image file, query file size, and calculate initial estimation."""
        clean_path = file_path
        if clean_path.startswith("file:///"):
            clean_path = clean_path[8:]
        elif clean_path.startswith("file:"):
            clean_path = clean_path[5:]

        p = Path(clean_path).resolve()
        if not p.is_file():
            logger.warning("CompressController cannot load missing file: %s", clean_path)
            return

        try:
            size = os.path.getsize(p)
            self._current_file_path = str(p)
            self._original_size_bytes = size
            self._last_output_path = ""
            self._progress = 0.0
            self._status_message = "Ready"

            logger.info("Loaded image for compression: %s (%d bytes)", p.name, size)
            self.imageChanged.emit()
            self.resultChanged.emit()

            self.refreshEstimation()
        except Exception as err:
            logger.error("Failed to inspect file size for %s: %s", p, err)
            if self._signals:
                self._signals.triggerError(
                    "Cannot Inspect Image",
                    f"Could not read file details for '{p.name}'.",
                    str(err),
                    "Select a valid image file.",
                )

    @Slot(int)
    def setQuality(self, val: int) -> None:
        """Update compression quality (1-100) and refresh size estimation."""
        clamped = max(1, min(100, val))
        if self._quality == clamped:
            return
        self._quality = clamped
        self.optionsChanged.emit()
        self.refreshEstimation()

    @Slot(str)
    def setTargetFormat(self, fmt: str) -> None:
        """Update target format ('original', 'webp', 'jpeg', 'png')."""
        if self._target_format == fmt:
            return
        self._target_format = fmt
        self.optionsChanged.emit()
        self.refreshEstimation()

    @Slot(bool)
    def setStripMetadata(self, val: bool) -> None:
        """Toggle metadata removal."""
        if self._strip_metadata == val:
            return
        self._strip_metadata = val
        self.optionsChanged.emit()
        self.refreshEstimation()

    @Slot(bool)
    def setPngQuantize(self, val: bool) -> None:
        """Toggle PNG palette quantization."""
        if self._png_quantize == val:
            return
        self._png_quantize = val
        self.optionsChanged.emit()
        self.refreshEstimation()

    @Slot()
    def refreshEstimation(self) -> None:
        """Compute estimated compressed size without altering the original file."""
        if not self._current_file_path or self._original_size_bytes <= 0:
            self._estimated_size_bytes = 0
            self._estimated_reduction = 0.0
            self.estimationChanged.emit()
            return

        try:
            opts = CompressOptions(
                quality=self._quality,
                target_format=self._target_format,
                strip_metadata=self._strip_metadata,
                png_quantize=self._png_quantize,
            )
            est_size, reduction = self._service.estimate_compression(self._current_file_path, opts)
            self._estimated_size_bytes = est_size
            self._estimated_reduction = reduction
            self.estimationChanged.emit()
        except Exception as err:
            logger.warning("Could not calculate compression estimation: %s", err)

    @Slot(result=str)
    def executeCompress(self, output_dir: str = "") -> str:
        """Dispatch async compression to background thread pool."""
        if not self._current_file_path or self._original_size_bytes <= 0:
            if self._signals:
                self._signals.triggerError(
                    "No Image Selected",
                    "Please select or drop an image before executing compression.",
                    "No image file is currently loaded in the workspace.",
                    "Choose an image using the file picker or drag and drop.",
                )
            return ""

        if self._is_processing:
            logger.warning("Compress operation already in progress.")
            return ""

        opts = CompressOptions(
            quality=self._quality,
            target_format=self._target_format,
            strip_metadata=self._strip_metadata,
            png_quantize=self._png_quantize,
        )

        dest_path = None
        if output_dir:
            dest_path = str(
                self._service.get_default_output_path(
                    self._current_file_path,
                    output_dir=output_dir,
                    target_format=self._target_format,
                )
            )

        self._is_processing = True
        self._progress = 0.0
        self._status_message = "Starting compression..."
        self.processingStateChanged.emit()
        self.progressChanged.emit()

        if self._signals:
            self._signals.taskProgress.emit("task-compress", 0.0, "Starting compression...")

        def run_compress(progress_callback: Any = None) -> CompressResult:
            return self._service.execute(
                input_path=self._current_file_path,
                output_path=dest_path,
                options=opts,
                progress_callback=progress_callback,
            )

        worker = ImageWorker(run_compress, task_id="task-compress")
        self._current_worker = worker

        worker.signals.progress.connect(self._on_progress)
        worker.signals.finished.connect(self._on_finished)
        worker.signals.error.connect(self._on_error)
        worker.signals.cancelled.connect(self._on_cancelled)

        submit_worker(worker)
        return worker.task_id

    @Slot()
    def cancel(self) -> None:
        """Cancel running background compression."""
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
        if isinstance(result, CompressResult):
            self._last_output_path = result.output_path
            self._status_message = f"Compressed (-{result.reduction_percent}%)"
            self.resultChanged.emit()
            self.processingStateChanged.emit()
            self.compressFinished.emit(task_id, result.output_path)

            if self._signals:
                self._signals.taskCompleted.emit(task_id, result.output_path)
                self._signals.showToast(
                    "success",
                    "Compression Complete",
                    f"Saved {Path(result.output_path).name} (-{result.reduction_percent}%)",
                    3000,
                )

    def _on_error(self, task_id: str, error_name: str, error_message: str) -> None:
        self._is_processing = False
        self._current_worker = None
        self._status_message = f"Failed: {error_message}"
        self.processingStateChanged.emit()
        self.compressFailed.emit(task_id, error_message)

        if self._signals:
            self._signals.taskFailed.emit(task_id, error_message)
            self._signals.triggerError(
                "Compression Operation Failed",
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
                "info", "Compression Cancelled", "Operation was cancelled.", 2000
            )
