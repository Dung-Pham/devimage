"""Asynchronous image task worker wrapping QRunnable with Qt signals."""

from __future__ import annotations

import inspect
import uuid
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, Signal

from devimage.app.logging import get_logger

logger = get_logger("workers.image_worker")


class WorkerSignals(QObject):
    """Signal carrier for QRunnable tasks delivering updates across thread boundaries."""

    # Emitted when execution starts: taskId (str)
    started = Signal(str)

    # Emitted during execution: taskId (str), progress (float 0.0 - 100.0), message (str)
    progress = Signal(str, float, str)

    # Emitted when execution succeeds: taskId (str), result (object)
    finished = Signal(str, object)

    # Emitted when execution raises an unhandled exception: taskId (str), errorName (str), errorMessage (str)
    error = Signal(str, str, str)

    # Emitted if execution was cancelled: taskId (str)
    cancelled = Signal(str)


class ImageWorker(QRunnable):
    """Generic asynchronous task runner executing a callable on the background QThreadPool."""

    def __init__(
        self,
        fn: Callable[..., Any],
        *args: Any,
        task_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.task_id = task_id or str(uuid.uuid4())
        self.signals = WorkerSignals()
        self._is_cancelled = False
        self.setAutoDelete(True)

    @property
    def is_cancelled(self) -> bool:
        """Check whether task cancellation has been requested."""
        return self._is_cancelled

    def cancel(self) -> None:
        """Request task cancellation."""
        self._is_cancelled = True
        logger.info("Cancellation requested for worker task %s", self.task_id)

    def _progress_reporter(self, progress: float, message: str = "") -> None:
        """Callback passed to workers supporting granular progress reporting."""
        if not self._is_cancelled:
            self.signals.progress.emit(self.task_id, float(progress), message)

    def run(self) -> None:
        """Execute the worker payload on the worker thread."""
        if self._is_cancelled:
            self.signals.cancelled.emit(self.task_id)
            return

        self.signals.started.emit(self.task_id)

        try:
            # Check if target callable accepts a progress_callback or cancel_check argument
            sig = inspect.signature(self.fn)
            params = sig.parameters

            call_kwargs = dict(self.kwargs)
            if "progress_callback" in params and "progress_callback" not in call_kwargs:
                call_kwargs["progress_callback"] = self._progress_reporter
            if "cancel_check" in params and "cancel_check" not in call_kwargs:
                call_kwargs["cancel_check"] = lambda: self._is_cancelled

            result = self.fn(*self.args, **call_kwargs)

            if self._is_cancelled:
                self.signals.cancelled.emit(self.task_id)
            else:
                self.signals.finished.emit(self.task_id, result)
        except Exception as err:
            logger.exception("Worker task %s encountered an error: %s", self.task_id, err)
            self.signals.error.emit(self.task_id, type(err).__name__, str(err))
