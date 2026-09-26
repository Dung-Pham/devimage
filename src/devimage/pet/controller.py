"""Qt bridge for the desktop AI pet."""

from __future__ import annotations

from PySide6.QtCore import QObject, Property, QThread, Signal, Slot

from devimage.pet.ai_service import PetAIError, PetAIService


class _ReplyWorker(QThread):
    """Perform network I/O away from the Qt GUI thread."""

    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, service: PetAIService, history: list[dict[str, str]]) -> None:
        super().__init__()
        self._service = service
        self._history = history

    def run(self) -> None:
        try:
            self.succeeded.emit(self._service.reply(self._history))
        except PetAIError as exc:
            self.failed.emit(str(exc))


class PetController(QObject):
    """Expose pet state and chat actions to QML."""

    replyReceived = Signal(str)
    errorOccurred = Signal(str)
    busyChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._service = PetAIService()
        self._busy = False
        self._history: list[dict[str, str]] = []
        self._worker: _ReplyWorker | None = None

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(bool, constant=True)
    def configured(self) -> bool:
        return self._service.configured

    @Property(str, constant=True)
    def model(self) -> str:
        return self._service.model

    @Slot(str)
    def ask(self, message: str) -> None:
        message = message.strip()
        if not message or self._busy:
            return

        self._history.append({"role": "user", "content": message})
        self._set_busy(True)
        self._worker = _ReplyWorker(self._service, list(self._history))
        self._worker.succeeded.connect(self._on_success)
        self._worker.failed.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_success(self, reply: str) -> None:
        self._history.append({"role": "assistant", "content": reply})
        self.replyReceived.emit(reply)

    def _on_error(self, message: str) -> None:
        self.errorOccurred.emit(message)

    def _on_finished(self) -> None:
        self._set_busy(False)
        self._worker = None

    def _set_busy(self, value: bool) -> None:
        if self._busy == value:
            return
        self._busy = value
        self.busyChanged.emit()

