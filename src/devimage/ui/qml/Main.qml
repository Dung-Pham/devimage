import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "dialogs"

ApplicationWindow {
    id: window
    width: backend ? backend.settings.get("window_width", 1100) : 1100
    height: backend ? backend.settings.get("window_height", 720) : 720
    minimumWidth: 800
    minimumHeight: 560
    visible: true
    title: (backend ? backend.appName : "DevImage") + " — Developer Image Toolbox"
    color: "#0f1117"

    // Property bindings and state
    property string activeTheme: backend ? backend.settings.get("theme", "dark") : "dark"

    // Escape shortcut to return home from any tool
    Shortcut {
        sequence: "Escape"
        onActivated: {
            if (appShell.currentRoute !== "home") {
                appShell.navigateToHome()
            }
        }
    }

    // Ctrl+, shortcut to open settings
    Shortcut {
        sequence: "Ctrl+,"
        onActivated: settingsDialog.open()
    }

    // Embed Modular Application Shell
    AppShell {
        id: appShell
        anchors.fill: parent
        onSettingsRequested: settingsDialog.open()
    }

    // Global Signal Listeners for Toast & Dialogs
    Connections {
        target: backend ? backend.signals : null

        function onNotify(type, title, message, duration_ms) {
            toastBanner.show(type, title, message, duration_ms)
        }

        function onErrorOccurred(title, description, cause, suggested_action) {
            errorDialog.openError(title, description, cause, suggested_action)
        }
    }

    // Common Presentation Overlays
    ToastBanner {
        id: toastBanner
    }

    ErrorDialog {
        id: errorDialog
    }

    SettingsDialog {
        id: settingsDialog
    }
}
