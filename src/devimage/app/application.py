"""DevImage desktop application engine and PySide6 lifecycle coordinator."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

import devimage
from devimage.app.logging import get_logger
from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge
from devimage.tools.compress.controller import CompressController
from devimage.tools.compress.service import CompressService
from devimage.tools.convert.controller import ConvertController
from devimage.tools.convert.service import ConvertService
from devimage.tools.crop.controller import CropController
from devimage.tools.crop.service import CropService
from devimage.tools.inspector.controller import InspectorController
from devimage.tools.inspector.service import InspectorService
from devimage.tools.resize.controller import ResizeController
from devimage.tools.resize.service import ResizeService

logger = get_logger("application")


class BackendBridge(QObject):
    """Bridge object exposed directly to the QML root context."""

    def __init__(
        self,
        signals: AppSignalBridge,
        settings: SettingsManager,
        resize_controller: ResizeController | None = None,
        compress_controller: CompressController | None = None,
        convert_controller: ConvertController | None = None,
        crop_controller: CropController | None = None,
        inspector_controller: InspectorController | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._signals = signals
        self._settings = settings
        self._resize_controller = resize_controller
        self._compress_controller = compress_controller
        self._convert_controller = convert_controller
        self._crop_controller = crop_controller
        self._inspector_controller = inspector_controller

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

    @Property(QObject, constant=True)
    def resizeController(self) -> ResizeController | None:
        """Access to the image resize tool controller."""
        return self._resize_controller

    @Property(QObject, constant=True)
    def compressController(self) -> CompressController | None:
        """Access to the image compress tool controller."""
        return self._compress_controller

    @Property(QObject, constant=True)
    def convertController(self) -> ConvertController | None:
        """Access to the image convert tool controller."""
        return self._convert_controller

    @Property(QObject, constant=True)
    def cropController(self) -> CropController | None:
        """Access to the image crop tool controller."""
        return self._crop_controller

    @Property(QObject, constant=True)
    def inspectorController(self) -> InspectorController | None:
        """Access to the image metadata inspector controller."""
        return self._inspector_controller

    @Slot(str, result=str)
    def urlToPath(self, file_url: str) -> str:
        """Convert a file:// QUrl string to a local filesystem path."""
        if file_url.startswith("file:"):
            return QUrl(file_url).toLocalFile()
        return file_url

    @Slot(str, result=str)
    def pathToUrl(self, file_path: str) -> str:
        """Convert a local filesystem path to a file:// QUrl string for QML Image elements."""
        if not file_path:
            return ""
        if (
            file_path.startswith("file:")
            or file_path.startswith("qrc:")
            or file_path.startswith("http:")
            or file_path.startswith("https:")
        ):
            return file_path
        return QUrl.fromLocalFile(file_path).toString()

    @Slot(str, result=bool)
    def validateImageFile(self, file_path: str) -> bool:
        """Verify that the path points to a file with a supported image extension."""
        supported_exts = {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
            ".tiff",
            ".tif",
            ".gif",
            ".ico",
            ".avif",
        }
        path = Path(file_path)
        return path.is_file() and path.suffix.lower() in supported_exts

    @Slot(str)
    def openImageFile(self, file_path: str) -> None:
        """Validate, record in recent files, and emit selection signal."""
        clean_path = self.urlToPath(file_path)
        if not self.validateImageFile(clean_path):
            self._signals.triggerError(
                "Invalid Image File",
                f"File '{clean_path}' is not a supported or existing image.",
                "The file extension is unsupported or the file does not exist.",
                "Please select a PNG, JPEG, WebP, BMP, TIFF, GIF, ICO, or AVIF image file.",
            )
            return

        self._settings.addRecentFile(clean_path)
        self._signals.fileSelected.emit(clean_path)
        self._signals.showToast("info", "Image Loaded", Path(clean_path).name, 2500)


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
        self.resize_service = ResizeService()
        self.resize_controller = ResizeController(
            service=self.resize_service,
            signals=self.signals,
            settings=self.settings,
        )
        self.compress_service = CompressService()
        self.compress_controller = CompressController(
            service=self.compress_service,
            signals=self.signals,
            settings=self.settings,
        )
        self.convert_service = ConvertService()
        self.convert_controller = ConvertController(
            service=self.convert_service,
            signals=self.signals,
            settings=self.settings,
        )
        self.crop_service = CropService()
        self.crop_controller = CropController(
            service=self.crop_service,
            signals=self.signals,
            settings=self.settings,
        )
        self.inspector_service = InspectorService()
        self.inspector_controller = InspectorController(
            service=self.inspector_service,
            signals=self.signals,
            settings=self.settings,
        )
        self.backend = BackendBridge(
            signals=self.signals,
            settings=self.settings,
            resize_controller=self.resize_controller,
            compress_controller=self.compress_controller,
            convert_controller=self.convert_controller,
            crop_controller=self.crop_controller,
            inspector_controller=self.inspector_controller,
        )

        self.engine = QQmlApplicationEngine()
        self.engine.rootContext().setContextProperty("backend", self.backend)
        self.engine.rootContext().setContextProperty("resizeController", self.resize_controller)
        self.engine.rootContext().setContextProperty("compressController", self.compress_controller)
        self.engine.rootContext().setContextProperty("convertController", self.convert_controller)
        self.engine.rootContext().setContextProperty("cropController", self.crop_controller)
        self.engine.rootContext().setContextProperty(
            "inspectorController", self.inspector_controller
        )

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
