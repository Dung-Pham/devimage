import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

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

    // Embed Modular Application Shell
    AppShell {
        id: appShell
        anchors.fill: parent
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

    // Toast Notification Banner Component
    Rectangle {
        id: toastBanner
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 48
        height: 48
        radius: 8
        visible: opacity > 0
        opacity: 0.0
        color: toastType === "error" ? "#7f1d1d" : (toastType === "success" ? "#064e3b" : "#1e293b")
        border.color: toastType === "error" ? "#ef4444" : (toastType === "success" ? "#10b981" : "#475569")
        implicitWidth: toastContent.implicitWidth + 32

        property string toastType: "info"

        RowLayout {
            id: toastContent
            anchors.centerIn: parent
            spacing: 10

            Text {
                id: toastTitle
                font.bold: true
                font.pixelSize: 13
                color: "#ffffff"
            }
            Text {
                id: toastMsg
                font.pixelSize: 13
                color: "#e2e8f0"
            }
        }

        NumberAnimation on opacity {
            id: toastAnim
            duration: 250
        }

        Timer {
            id: toastTimer
            onTriggered: {
                toastAnim.to = 0.0
                toastAnim.restart()
            }
        }

        function show(type, title, message, duration_ms) {
            toastType = type
            toastTitle.text = title
            toastMsg.text = message
            toastAnim.to = 1.0
            toastAnim.restart()
            toastTimer.interval = duration_ms > 0 ? duration_ms : 3000
            toastTimer.restart()
        }
    }

    // Error Dialog Component (Plan Section 19 structured error view)
    Dialog {
        id: errorDialog
        anchors.centerIn: parent
        width: 480
        modal: true
        title: "Error"

        property string errTitle: ""
        property string errDesc: ""
        property string errCause: ""
        property string errAction: ""

        background: Rectangle {
            color: "#161922"
            radius: 12
            border.color: "#ef4444"
        }

        contentItem: ColumnLayout {
            spacing: 14
            Text {
                text: errorDialog.errTitle
                font.pixelSize: 18
                font.bold: true
                color: "#ef4444"
            }
            Text {
                text: errorDialog.errDesc
                font.pixelSize: 14
                color: "#f8fafc"
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            Rectangle { Layout.fillWidth: true; height: 1; color: "#262b3a" }
            ColumnLayout {
                spacing: 4
                Text { text: "Possible Cause:"; font.bold: true; font.pixelSize: 12; color: "#94a3b8" }
                Text { text: errorDialog.errCause; font.pixelSize: 13; color: "#cbd5e1"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            }
            ColumnLayout {
                spacing: 4
                Text { text: "Suggested Action:"; font.bold: true; font.pixelSize: 12; color: "#94a3b8" }
                Text { text: errorDialog.errAction; font.pixelSize: 13; color: "#38bdf8"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            }
            Button {
                text: "Dismiss"
                Layout.alignment: Qt.AlignRight
                onClicked: errorDialog.close()
            }
        }

        function openError(title, description, cause, action) {
            errTitle = title
            errDesc = description
            errCause = cause
            errAction = action
            open()
        }
    }
}
