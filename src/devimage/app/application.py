"""DevImage desktop application engine and PySide6 lifecycle coordinator."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

import devimage
from devimage.app.logging import get_logger
from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge

logger = get_logger("application")


class BackendBridge(QObject):
    """Bridge object exposed directly to the QML root context."""

    def __init__(
        self,
        signals: AppSignalBridge,
        settings: SettingsManager,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._signals = signals
        self._settings = settings

    @Property(str, constant=True)
    def appName(self) -> str:
        """Application display name."""
        return devimage.__app_name__

    @Property(str, constant=True)
    def appVersion(self) -> str:
        """Application semantic version."""
        return devimage.__version__

    @Property(QObject, constant=True)
    def signals(self) -> AppSignalBridge:
        """Access to the global signal and notification bridge."""
        return self._signals

    @Property(QObject, constant=True)
    def settings(self) -> SettingsManager:
        """Access to the persistent application settings manager."""
        return self._settings


class DevImageApp:
    """Encapsulates the PySide6 QGuiApplication and QQmlApplicationEngine."""

    def __init__(self, argv: list[str] | None = None) -> None:
        if argv is None:
            argv = sys.argv

        self.qt_app = QGuiApplication.instance()
        if self.qt_app is None:
            self.qt_app = QGuiApplication(argv)
            self.qt_app.setApplicationName(devimage.__app_name__)
            self.qt_app.setOrganizationName("DevImage")
            self.qt_app.setApplicationVersion(devimage.__version__)

        QQuickStyle.setStyle("Basic")

        self.signals = AppSignalBridge()
        self.settings = SettingsManager()
        self.backend = BackendBridge(signals=self.signals, settings=self.settings)

        self.engine = QQmlApplicationEngine()
        self.engine.rootContext().setContextProperty("backend", self.backend)

        self._qml_path = Path(__file__).resolve().parent.parent / "ui" / "qml" / "Main.qml"

    def load_qml(self) -> bool:
        """Load Main.qml into the QML application engine."""
        logger.info("Loading QML interface from %s", self._qml_path)
        if not self._qml_path.exists():
            logger.error("Main.qml not found at %s", self._qml_path)
            return False

        self.engine.load(QUrl.fromLocalFile(str(self._qml_path)))
        if not self.engine.rootObjects():
            logger.error("Failed to load QML root object.")
            return False

        logger.info("QML interface loaded successfully.")
        return True

    def exec(self) -> int:
        """Execute the Qt GUI main event loop."""
        return self.qt_app.exec()
