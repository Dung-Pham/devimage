"""PySide6 controller bridging the Crop Service to QML presentation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from devimage.app.logging import get_logger
from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge
from devimage.engine.image.metadata import extract_metadata
from devimage.tools.crop.service import CropOptions, CropResult, CropService
from devimage.workers.image_worker import ImageWorker
from devimage.workers.pool import submit_worker

logger = get_logger("tools.crop.controller")

ASPECT_RATIO_PRESETS: dict[str, tuple[int, int] | None] = {
    "free": None,
    "1:1": (1, 1),
    "4:3": (4, 3),
    "3:4": (3, 4),
    "16:9": (16, 9),
    "9:16": (9, 16),
}


class CropController(QObject):
    """QObject controller managing crop box geometry, aspect ratios, rotation, and execution."""

    imageChanged = Signal()
    cropRectChanged = Signal()
    orientationChanged = Signal()
    processingStateChanged = Signal()
    progressChanged = Signal()
    resultChanged = Signal()

    cropFinished = Signal(str, str)  # taskId, outputPath
    cropFailed = Signal(str, str)  # taskId, errorMessage

    def __init__(
        self,
        service: CropService | None = None,
        signals: AppSignalBridge | None = None,
        settings: SettingsManager | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service or CropService()
        self._signals = signals
        self._settings = settings

        # Image state
        self._current_file_path: str = ""
        self._original_width: int = 0
        self._original_height: int = 0
        self._rotation: int = 0

        # Normalized crop rectangle (0.0 - 1.0)
        self._crop_x: float = 0.0
        self._crop_y: float = 0.0
        self._crop_width: float = 1.0
        self._crop_height: float = 1.0
        self._aspect_ratio_mode: str = "free"

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
        return bool(self._current_file_path and self._original_width > 0)

    @Property(int, notify=imageChanged)
    def originalWidth(self) -> int:
        return self._original_width

    @Property(int, notify=imageChanged)
    def originalHeight(self) -> int:
        return self._original_height

    @Property(int, notify=orientationChanged)
    def currentWidth(self) -> int:
        if self._rotation in (90, 270):
            return self._original_height
        return self._original_width

    @Property(int, notify=orientationChanged)
    def currentHeight(self) -> int:
        if self._rotation in (90, 270):
            return self._original_width
        return self._original_height

    @Property(int, notify=orientationChanged)
    def rotation(self) -> int:
        return self._rotation

    @Property(float, notify=cropRectChanged)
    def cropX(self) -> float:
        return self._crop_x

    @Property(float, notify=cropRectChanged)
    def cropY(self) -> float:
        return self._crop_y

    @Property(float, notify=cropRectChanged)
    def cropWidth(self) -> float:
        return self._crop_width

    @Property(float, notify=cropRectChanged)
    def cropHeight(self) -> float:
        return self._crop_height

    @Property(str, notify=cropRectChanged)
    def aspectRatioMode(self) -> str:
        return self._aspect_ratio_mode

    @Property(int, notify=cropRectChanged)
    def pixelCropWidth(self) -> int:
        return max(1, round(self._crop_width * self.currentWidth))

    @Property(int, notify=cropRectChanged)
    def pixelCropHeight(self) -> int:
        return max(1, round(self._crop_height * self.currentHeight))

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
        """Load image file, query dimensions, and reset crop geometry."""
        clean_path = file_path
        if clean_path.startswith("file:///"):
            clean_path = clean_path[8:]
        elif clean_path.startswith("file:"):
            clean_path = clean_path[5:]

        p = Path(clean_path).resolve()
        if not p.is_file():
            logger.warning("CropController cannot load missing file: %s", clean_path)
            return

        try:
            meta = extract_metadata(p)
            self._current_file_path = str(p)
            self._original_width = meta.width
            self._original_height = meta.height
            self._rotation = 0
            self._crop_x = 0.0
            self._crop_y = 0.0
            self._crop_width = 1.0
            self._crop_height = 1.0
            self._aspect_ratio_mode = "free"
            self._last_output_path = ""
            self._progress = 0.0
            self._status_message = "Ready"

            logger.info("Loaded image for crop: %s (%dx%d)", p.name, meta.width, meta.height)
            self.imageChanged.emit()
            self.orientationChanged.emit()
            self.cropRectChanged.emit()
            self.resultChanged.emit()
        except Exception as err:
            logger.error("Failed to inspect dimensions for %s: %s", p, err)
            if self._signals:
                self._signals.triggerError(
                    "Cannot Load Image",
                    f"Could not read metadata for '{p.name}'.",
                    str(err),
                    "Select a valid image file.",
                )

    @Slot(float, float, float, float)
    def setNormalizedCrop(self, x: float, y: float, w: float, h: float) -> None:
        """Update normalized crop bounds with boundary clamping."""
        cx = max(0.0, min(0.99, x))
        cy = max(0.0, min(0.99, y))
        cw = max(0.01, min(1.0 - cx, w))
        ch = max(0.01, min(1.0 - cy, h))

        self._crop_x = cx
        self._crop_y = cy
        self._crop_width = cw
        self._crop_height = ch
        self.cropRectChanged.emit()

    @Slot(str)
    def setAspectRatioMode(self, mode: str) -> None:
        """Change aspect ratio mode and snap current crop rectangle."""
        self._aspect_ratio_mode = mode
        if mode == "free":
            self.cropRectChanged.emit()
            return

        cur_w = self.currentWidth
        cur_h = self.currentHeight
        if cur_w <= 0 or cur_h <= 0:
            return

        if mode == "original":
            aspect_w, aspect_h = cur_w, cur_h
        elif mode in ASPECT_RATIO_PRESETS and ASPECT_RATIO_PRESETS[mode]:
            preset = ASPECT_RATIO_PRESETS[mode]
            assert preset is not None
            aspect_w, aspect_h = preset
        else:
            aspect_w, aspect_h = 1, 1

        left, top, right, bottom = self._service.calculate_center_crop(
            orig_w=cur_w, orig_h=cur_h, aspect_w=aspect_w, aspect_h=aspect_h
        )

        self._crop_x = left / cur_w
        self._crop_y = top / cur_h
        self._crop_width = (right - left) / cur_w
        self._crop_height = (bottom - top) / cur_h
        self.cropRectChanged.emit()

    @Slot()
    def centerCrop(self) -> None:
        """Re-center crop box on current image view."""
        self.setAspectRatioMode(self._aspect_ratio_mode)

    @Slot()
    def rotateClockwise(self) -> None:
        """Rotate image 90 degrees clockwise and reset crop box."""
        self._rotation = (self._rotation + 90) % 360
        self._crop_x = 0.0
        self._crop_y = 0.0
        self._crop_width = 1.0
        self._crop_height = 1.0
        self.orientationChanged.emit()
        self.cropRectChanged.emit()

    @Slot()
    def rotateCounterClockwise(self) -> None:
        """Rotate image 90 degrees counter-clockwise and reset crop box."""
        self._rotation = (self._rotation - 90) % 360
        self._crop_x = 0.0
        self._crop_y = 0.0
        self._crop_width = 1.0
        self._crop_height = 1.0
        self.orientationChanged.emit()
        self.cropRectChanged.emit()

    @Slot()
    def resetCrop(self) -> None:
        """Reset crop box to full image and rotation to 0."""
        self._rotation = 0
        self._crop_x = 0.0
        self._crop_y = 0.0
        self._crop_width = 1.0
        self._crop_height = 1.0
        self._aspect_ratio_mode = "free"
        self.orientationChanged.emit()
        self.cropRectChanged.emit()

    @Slot(result=str)
    def executeCrop(self, output_dir: str = "") -> str:
        """Dispatch async crop operation to background thread pool."""
        if not self._current_file_path or self._original_width <= 0:
            if self._signals:
                self._signals.triggerError(
                    "No Image Selected",
                    "Please select or drop an image before executing crop.",
                    "No image file is currently loaded in the workspace.",
                    "Choose an image using the file picker or drag and drop.",
                )
            return ""

        if self._is_processing:
            logger.warning("Crop operation already in progress.")
            return ""

        cur_w = self.currentWidth
        cur_h = self.currentHeight

        left = max(0, min(cur_w - 1, round(self._crop_x * cur_w)))
        top = max(0, min(cur_h - 1, round(self._crop_y * cur_h)))
        right = max(left + 1, min(cur_w, round((self._crop_x + self._crop_width) * cur_w)))
        bottom = max(top + 1, min(cur_h, round((self._crop_y + self._crop_height) * cur_h)))

        crop_box = (left, top, right, bottom)
        # If crop spans 100% of image with 0 rotation, skip redundant crop box
        if (
            self._crop_x == 0.0
            and self._crop_y == 0.0
            and self._crop_width == 1.0
            and self._crop_height == 1.0
            and self._rotation == 0
        ):
            crop_box = (0, 0, cur_w, cur_h)

        opts = CropOptions(
            crop_box=crop_box,
            rotation=self._rotation,
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
        self._status_message = "Starting crop..."
        self.processingStateChanged.emit()
        self.progressChanged.emit()

        if self._signals:
            self._signals.taskProgress.emit("task-crop", 0.0, "Starting crop...")

        def run_crop(progress_callback: Any = None) -> CropResult:
            return self._service.execute(
                input_path=self._current_file_path,
                output_path=dest_path,
                options=opts,
                progress_callback=progress_callback,
            )

        worker = ImageWorker(run_crop, task_id="task-crop")
        self._current_worker = worker

        worker.signals.progress.connect(self._on_progress)
        worker.signals.finished.connect(self._on_finished)
        worker.signals.error.connect(self._on_error)
        worker.signals.cancelled.connect(self._on_cancelled)

        submit_worker(worker)
        return worker.task_id

    @Slot()
    def cancel(self) -> None:
        """Cancel running background crop."""
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
        if isinstance(result, CropResult):
            self._last_output_path = result.output_path
            self._status_message = f"Cropped to {result.cropped_width}x{result.cropped_height}"
            self.resultChanged.emit()
            self.processingStateChanged.emit()
            self.cropFinished.emit(task_id, result.output_path)

            if self._signals:
                self._signals.taskCompleted.emit(task_id, result.output_path)
                self._signals.showToast(
                    "success",
                    "Crop Complete",
                    f"Saved {Path(result.output_path).name} ({result.cropped_width}x{result.cropped_height})",
                    3000,
                )

    def _on_error(self, task_id: str, error_name: str, error_message: str) -> None:
        self._is_processing = False
        self._current_worker = None
        self._status_message = f"Failed: {error_message}"
        self.processingStateChanged.emit()
        self.cropFailed.emit(task_id, error_message)

        if self._signals:
            self._signals.taskFailed.emit(task_id, error_message)
            self._signals.triggerError(
                "Crop Operation Failed",
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
            self._signals.showToast("info", "Crop Cancelled", "Operation was cancelled.", 2000)
