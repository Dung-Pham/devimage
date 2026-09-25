"""Headless GUI smoke tests verifying QML engine instantiation and Python-QML bridge."""

import pytest
from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication

from devimage.app.application import DevImageApp
from devimage.main import parse_args


@pytest.fixture
def app_instance():
    """Create a DevImageApp instance with offscreen platform."""
    app = DevImageApp([])
    yield app
    # Teardown: close engine root objects if any
    for obj in app.engine.rootObjects():
        obj.deleteLater()
    QGuiApplication.processEvents()


def test_app_init_and_qml_load(app_instance: DevImageApp):
    """Verify application initializes and loads Main.qml cleanly."""
    success = app_instance.load_qml()
    assert success is True

    roots = app_instance.engine.rootObjects()
    assert len(roots) == 1
    root = roots[0]
    assert root is not None

    # Check window title and dimensions
    title = root.property("title")
    assert "DevImage" in title
    assert root.property("minimumWidth") == 800
    assert root.property("minimumHeight") == 560


def test_backend_bridge_in_qml(app_instance: DevImageApp):
    """Verify backend bridge properties and signals are accessible to QML."""
    assert app_instance.load_qml() is True
    root = app_instance.engine.rootObjects()[0]

    # Verify context property 'backend'
    backend = app_instance.backend
    assert backend.appName == "DevImage"
    assert backend.appVersion == "0.1.0"
    assert isinstance(backend.signals, QObject)
    assert isinstance(backend.settings, QObject)

    # Verify root window property bindings that depend on backend
    assert root.property("activeTheme") == "dark"


def test_python_qml_two_way_communication(app_instance: DevImageApp):
    """Verify two-way signal communication between Python and QML."""
    assert app_instance.load_qml() is True

    # 1. Trigger signal from Python bridge
    received_toasts = []
    app_instance.signals.notify.connect(
        lambda t, title, m, d: received_toasts.append((t, title, m, d))
    )

    app_instance.signals.showToast("info", "Test Toast", "Smoke test verification", 1500)
    QGuiApplication.processEvents()

    assert len(received_toasts) == 1
    assert received_toasts[0][0] == "info"
    assert received_toasts[0][1] == "Test Toast"

    # 2. Trigger error dialog signal
    received_errors = []
    app_instance.signals.errorOccurred.connect(
        lambda t, desc, c, a: received_errors.append((t, desc, c, a))
    )

    app_instance.signals.triggerError(
        "Smoke Test Title",
        "Smoke Test Description",
        "Smoke Test Cause",
        "Smoke Test Action",
    )
    QGuiApplication.processEvents()

    assert len(received_errors) == 1
    assert received_errors[0][0] == "Smoke Test Title"


def test_cli_parsing():
    """Verify command line flags parse correctly."""
    args = parse_args(["--debug"])
    assert args.debug is True

    default_args = parse_args([])
    assert default_args.debug is False
