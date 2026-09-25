"""Central communication layer and Qt signal bridge between Python and QML.

Ensures clean separation of concerns: background services communicate via Qt Signals,
and QML views react to state transitions without coupling to backend implementations.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from devimage.app.logging import get_logger

logger = get_logger("signals")


class AppSignalBridge(QObject):
    """Central Qt signal broker registered with the QML application engine."""

    # 1. UI Notification & Toast Signals
    # Arguments: type (str), title (str), message (str), duration_ms (int)
    notify = Signal(str, str, str, int)

    # 2. Structured Error Signals
    # Arguments: title (str), description (str), cause (str), suggested_action (str)
    errorOccurred = Signal(str, str, str, str)

    # 3. Navigation & Tool Selection Signals
    # Arguments: toolId (str)
    toolActivated = Signal(str)

    # Arguments: route (str) e.g., "home", "settings", "tool"
    navigated = Signal(str)

    # 4. Asynchronous Task & Worker Signals
    # Arguments: taskId (str), progress (float 0-100), message (str)
    taskProgress = Signal(str, float, str)

    # Arguments: taskId (str), outputPath (str)
    taskCompleted = Signal(str, str)

    # Arguments: taskId (str), errorMessage (str)
    taskFailed = Signal(str, str)

    # 5. File / Batch Signals
    # Arguments: filePath (str)
    fileSelected = Signal(str)

    # -------------------------------------------------------------------------
    # QML Invocable Slots
    # -------------------------------------------------------------------------

    @Slot(str, str, str, int)
    def showToast(self, toast_type: str, title: str, message: str = "", duration_ms: int = 3000) -> None:
        """Trigger a toast notification from Python or QML."""
        logger.debug("Toast emitted: [%s] %s - %s", toast_type, title, message)
        self.notify.emit(toast_type, title, message, duration_ms)

    @Slot(str, str, str, str)
    def triggerError(self, title: str, description: str, cause: str, suggested_action: str) -> None:
        """Trigger a structured user-facing error modal dialog."""
        logger.warning("Error dialog triggered: %s: %s", title, description)
        self.errorOccurred.emit(title, description, cause, suggested_action)

    @Slot(str)
    def selectTool(self, tool_id: str) -> None:
        """Switch active tool view in QML AppShell."""
        logger.info("Tool activated: %s", tool_id)
        self.toolActivated.emit(tool_id)

    @Slot(str)
    def navigate(self, route: str) -> None:
        """Navigate to a top-level route (e.g., 'home', 'settings')."""
        logger.info("Navigating to: %s", route)
        self.navigated.emit(route)

    @Slot(str, float, str)
    def updateTaskProgress(self, task_id: str, progress: float, message: str = "") -> None:
        """Relay progress update from worker threads."""
        self.taskProgress.emit(task_id, progress, message)

    @Slot(str, str)
    def reportTaskCompleted(self, task_id: str, output_path: str) -> None:
        """Relay task completion."""
        logger.info("Task %s completed. Output: %s", task_id, output_path)
        self.taskCompleted.emit(task_id, output_path)

    @Slot(str, str)
    def reportTaskFailed(self, task_id: str, error_message: str) -> None:
        """Relay task failure."""
        logger.error("Task %s failed: %s", task_id, error_message)
        self.taskFailed.emit(task_id, error_message)
