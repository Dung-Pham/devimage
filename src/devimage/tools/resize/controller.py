"""PySide6 controller bridging the Resize Service to QML presentation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from devimage.app.logging import get_logger
from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge
from devimage.engine.image.metadata import extract_metadata
from devimage.tools.resize.service import ResizeOptions, ResizeResult, ResizeService
from devimage.workers.image_worker import ImageWorker
from devimage.workers.pool import submit_worker

logger = get_logger("tools.resize.controller")


class ResizeController(QObject):
    """QObject controller managing state, options, and async processing for ResizeTool."""

    dimensionsChanged = Signal()
    optionsChanged = Signal()
    processingStateChanged = Signal()
    progressChanged = Signal()
    resultChanged = Signal()

    resizeFinished = Signal(str, str)  # taskId, outputPath
    resizeFailed = Signal(str, str)  # taskId, errorMessage

    def __init__(
        self,
        service: ResizeService | None = None,
        signals: AppSignalBridge | None = None,
        settings: SettingsManager | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service or ResizeService()
        self._signals = signals
        self._settings = settings

        # Image state
        self._current_file_path: str = ""
        self._original_width: int = 0
        self._original_height: int = 0
        self._target_width: int = 0
        self._target_height: int = 0

        # Options state
        self._keep_aspect: bool = True
        self._dont_enlarge: bool = False
        self._mode: str = "contain"  # "contain", "cover", "stretch"

        # Worker / Processing state
        self._is_processing: bool = False
        self._progress: float = 0.0
        self._status_message: str = ""
        self._last_output_path: str = ""
        self._current_worker: ImageWorker | None = None

    # --- Properties ---

    @Property(str, notify=dimensionsChanged)
    def currentFilePath(self) -> str:
        return self._current_file_path

    @Property(bool, notify=dimensionsChanged)
    def hasImage(self) -> bool:
        return bool(self._current_file_path and self._original_width > 0)

    @Property(int, notify=dimensionsChanged)
    def originalWidth(self) -> int:
        return self._original_width

    @Property(int, notify=dimensionsChanged)
    def originalHeight(self) -> int:
        return self._original_height

    @Property(int, notify=dimensionsChanged)
    def targetWidth(self) -> int:
        return self._target_width

    @Property(int, notify=dimensionsChanged)
    def targetHeight(self) -> int:
        return self._target_height

    @Property(bool, notify=optionsChanged)
    def keepAspect(self) -> bool:
        return self._keep_aspect

    @Property(bool, notify=optionsChanged)
    def dontEnlarge(self) -> bool:
        return self._dont_enlarge

    @Property(str, notify=optionsChanged)
    def mode(self) -> str:
        return self._mode

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
        """Load image metadata, reset dimensions, and notify UI."""
        clean_path = file_path
        if clean_path.startswith("file:///"):
            clean_path = clean_path[8:]
        elif clean_path.startswith("file:"):
            clean_path = clean_path[5:]

        p = Path(clean_path).resolve()
        if not p.is_file():
            logger.warning("ResizeController cannot load missing file: %s", clean_path)
            return

        try:
            meta = extract_metadata(p)
            self._current_file_path = str(p)
            self._original_width = meta.width
            self._original_height = meta.height
            self._target_width = meta.width
            self._target_height = meta.height
            self._last_output_path = ""
            self._progress = 0.0
            self._status_message = "Ready"

            logger.info(
                "Loaded image into ResizeController: %s (%dx%d)", p.name, meta.width, meta.height
            )
            self.dimensionsChanged.emit()
            self.resultChanged.emit()
        except Exception as err:
            logger.error("Failed to load image metadata for %s: %s", p, err)
            if self._signals:
                self._signals.triggerError(
                    "Cannot Load Image",
                    f"Could not read metadata for '{p.name}'.",
                    str(err),
                    "Select a valid image file.",
                )

    @Slot(int)
    def setTargetWidth(self, width: int) -> None:
        """Update target width and recalculate height if aspect ratio is locked."""
        if width <= 0 or width == self._target_width:
            return

        self._target_width = width
        if self._keep_aspect and self._original_width > 0 and self._original_height > 0:
            aspect = self._original_width / self._original_height
            self._target_height = max(1, round(width / aspect))

        self.dimensionsChanged.emit()

    @Slot(int)
    def setTargetHeight(self, height: int) -> None:
        """Update target height and recalculate width if aspect ratio is locked."""
        if height <= 0 or height == self._target_height:
            return

        self._target_height = height
        if self._keep_aspect and self._original_width > 0 and self._original_height > 0:
            aspect = self._original_width / self._original_height
            self._target_width = max(1, round(height * aspect))

        self.dimensionsChanged.emit()

    @Slot(int)
    def applyPreset(self, max_dim: int) -> None:
        """Apply a standard resolution preset (e.g. 1920, 1600, 1200, 1024, 768, 480)."""
        if self._original_width <= 0 or self._original_height <= 0:
            self._target_width = max_dim
            self._target_height = max_dim
        else:
            w, h = self._service.calculate_preset(
                orig_w=self._original_width,
                orig_h=self._original_height,
                preset_max_dim=max_dim,
                keep_aspect=self._keep_aspect,
            )
            self._target_width = w
            self._target_height = h

        self.dimensionsChanged.emit()

    @Slot(bool)
    def setKeepAspect(self, enabled: bool) -> None:
        """Toggle aspect ratio preservation."""
        if self._keep_aspect == enabled:
            return
        self._keep_aspect = enabled
        if (
            enabled
            and self._original_width > 0
            and self._original_height > 0
            and self._target_width > 0
        ):
            aspect = self._original_width / self._original_height
            self._target_height = max(1, round(self._target_width / aspect))
            self.dimensionsChanged.emit()
        self.optionsChanged.emit()

    @Slot(bool)
    def setDontEnlarge(self, enabled: bool) -> None:
        """Toggle upscale prevention."""
        if self._dont_enlarge == enabled:
            return
        self._dont_enlarge = enabled
        self.optionsChanged.emit()

    @Slot(str)
    def setMode(self, mode: str) -> None:
        """Update resize mode: 'contain', 'cover', 'stretch'."""
        if mode not in ("contain", "cover", "stretch") or self._mode == mode:
            return
        self._mode = mode
        self.optionsChanged.emit()

    @Slot(result=str)
    def executeResize(self, output_dir: str = "") -> str:
        """Dispatch async resize operation to background thread pool."""
        if not self._current_file_path or self._original_width <= 0:
            if self._signals:
                self._signals.triggerError(
                    "No Image Selected",
                    "Please select or drop an image before executing resize.",
                    "No image file is currently loaded in the workspace.",
                    "Choose an image using the file picker or drag and drop.",
                )
            return ""

        if self._is_processing:
            logger.warning("Resize operation already in progress.")
            return ""

        # Calculate final constrained dimensions
        final_w, final_h = self._service.calculate_dimensions(
            orig_w=self._original_width,
            orig_h=self._original_height,
            target_w=self._target_width,
            target_h=self._target_height,
            keep_aspect=self._keep_aspect,
            dont_enlarge=self._dont_enlarge,
            mode=self._mode,
        )

        options = ResizeOptions(
            target_width=final_w,
            target_height=final_h,
            mode=self._mode,
            keep_aspect=self._keep_aspect,
            dont_enlarge=self._dont_enlarge,
            quality=self._settings.get("default_quality", 85) if self._settings else 85,
        )

        dest_path = None
        if output_dir:
            dest_path = str(
                self._service.get_default_output_path(
                    self._current_file_path, output_dir=output_dir
                )
            )

        self._is_processing = True
        self._progress = 0.0
        self._status_message = "Starting resize..."
        self.processingStateChanged.emit()
        self.progressChanged.emit()

        if self._signals:
            self._signals.taskProgress.emit("task-resize", 0.0, "Starting resize...")

        def run_resize(progress_callback: Any = None) -> ResizeResult:
            return self._service.execute(
                input_path=self._current_file_path,
                output_path=dest_path,
                options=options,
                progress_callback=progress_callback,
            )

        worker = ImageWorker(run_resize, task_id="task-resize")
        self._current_worker = worker

        worker.signals.progress.connect(self._on_progress)
        worker.signals.finished.connect(self._on_finished)
        worker.signals.error.connect(self._on_error)
        worker.signals.cancelled.connect(self._on_cancelled)

        submit_worker(worker)
        return worker.task_id

    @Slot()
    def cancel(self) -> None:
        """Cancel the running background resize task."""
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
        if isinstance(result, ResizeResult):
            self._last_output_path = result.output_path
            self._status_message = f"Resized ({result.target_width}x{result.target_height})"
            self.resultChanged.emit()
            self.processingStateChanged.emit()
            self.resizeFinished.emit(task_id, result.output_path)

            if self._signals:
                self._signals.taskCompleted.emit(task_id, result.output_path)
                self._signals.showToast(
                    "success",
                    "Resize Complete",
                    f"Saved {Path(result.output_path).name}",
                    3000,
                )

    def _on_error(self, task_id: str, error_name: str, error_message: str) -> None:
        self._is_processing = False
        self._current_worker = None
        self._status_message = f"Failed: {error_message}"
        self.processingStateChanged.emit()
        self.resizeFailed.emit(task_id, error_message)

        if self._signals:
            self._signals.taskFailed.emit(task_id, error_message)
            self._signals.triggerError(
                "Resize Operation Failed",
                error_message,
                f"Exception: {error_name}",
                "Please verify the image file format and permissions, then try again.",
            )

    def _on_cancelled(self, task_id: str) -> None:
        self._is_processing = False
        self._current_worker = None
        self._status_message = "Cancelled"
        self.processingStateChanged.emit()
        if self._signals:
            self._signals.showToast("info", "Resize Cancelled", "Operation was cancelled.", 2000)
