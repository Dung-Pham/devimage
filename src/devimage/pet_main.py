"""Launch the floating DevImage AI desktop pet."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from devimage.pet.controller import PetController


def main() -> int:
    app = QGuiApplication(sys.argv)
    app.setApplicationName("DevImage Pet")
    app.setOrganizationName("DevImage")

    controller = PetController()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("petController", controller)

    qml_path = Path(__file__).resolve().parent / "ui" / "qml" / "PetWindow.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

