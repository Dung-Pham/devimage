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
    property int pingCount: 0
    property string lastMessage: "Ready"
    property string activeTheme: backend ? backend.settings.get("theme", "dark") : "dark"

    // Listen to signal bridge
    Connections {
        target: backend ? backend.signals : null

        function onNotify(type, title, message, duration_ms) {
            toastBanner.show(type, title, message, duration_ms)
        }

        function onErrorOccurred(title, description, cause, suggested_action) {
            errorDialog.openError(title, description, cause, suggested_action)
        }
    }

    // Main Layout Shell
    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Top Navigation / Header Bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            color: "#161922"

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 1
                color: "#262b3a"
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 24
                anchors.rightMargin: 24
                spacing: 16

                // App Brand
                RowLayout {
                    spacing: 10
                    Rectangle {
                        width: 32
                        height: 32
                        radius: 8
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "#6366f1" }
                            GradientStop { position: 1.0; color: "#4f46e5" }
                        }
                        Text {
                            anchors.centerIn: parent
                            text: "D"
                            font.bold: true
                            font.pixelSize: 18
                            color: "#ffffff"
                        }
                    }

                    Text {
                        text: backend ? backend.appName : "DevImage"
                        font.pixelSize: 18
                        font.bold: true
                        color: "#f8fafc"
                    }

                    Rectangle {
                        width: 58
                        height: 20
                        radius: 10
                        color: "#1e293b"
                        border.color: "#334155"
                        Text {
                            anchors.centerIn: parent
                            text: "v" + (backend ? backend.appVersion : "0.1.0")
                            font.pixelSize: 11
                            color: "#94a3b8"
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                // Phase 0 Status Pill
                Rectangle {
                    height: 28
                    radius: 14
                    color: "#064e3b"
                    border.color: "#059669"
                    implicitWidth: statusRow.implicitWidth + 24

                    RowLayout {
                        id: statusRow
                        anchors.centerIn: parent
                        spacing: 6
                        Rectangle {
                            width: 8
                            height: 8
                            radius: 4
                            color: "#34d399"
                        }
                        Text {
                            text: "Phase 0 Foundation Active"
                            font.pixelSize: 12
                            font.bold: true
                            color: "#a7f3d0"
                        }
                    }
                }
            }
        }

        // Central Workspace / Status View
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.centerIn: parent
                spacing: 24
                width: Math.min(parent.width - 48, 640)

                // Foundation Card
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: cardContent.implicitHeight + 40
                    radius: 12
                    color: "#161922"
                    border.color: "#262b3a"

                    ColumnLayout {
                        id: cardContent
                        anchors.fill: parent
                        anchors.margins: 24
                        spacing: 16

                        Text {
                            text: "Autonomous Foundation & Engine"
                            font.pixelSize: 20
                            font.bold: true
                            color: "#f8fafc"
                        }

                        Text {
                            text: "DevImage runtime core initialized with PySide6 (Qt Quick), structured error handling, rotating file logging, persistent JSON settings, and non-blocking asynchronous signal architecture."
                            font.pixelSize: 14
                            color: "#94a3b8"
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                            lineHeight: 1.4
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: "#262b3a"
                        }

                        // Communication Verification Box
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 16

                            Button {
                                id: pingBtn
                                text: "Ping Python Signal Bridge"
                                font.pixelSize: 13
                                font.bold: true
                                
                                contentItem: Text {
                                    text: pingBtn.text
                                    font: pingBtn.font
                                    color: "#ffffff"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }

                                background: Rectangle {
                                    implicitWidth: 200
                                    implicitHeight: 40
                                    radius: 8
                                    color: pingBtn.down ? "#4338ca" : (pingBtn.hovered ? "#4f46e5" : "#6366f1")
                                }

                                onClicked: {
                                    window.pingCount++
                                    window.lastMessage = "Ping #" + window.pingCount + " dispatched from QML"
                                    if (backend) {
                                        backend.signals.showToast(
                                            "success",
                                            "Bridge Connected",
                                            "Two-way Python <-> QML communication verified (Ping #" + window.pingCount + ")",
                                            3000
                                        )
                                    }
                                }
                            }

                            ColumnLayout {
                                spacing: 4
                                Text {
                                    text: "Communication Status:"
                                    font.pixelSize: 12
                                    color: "#64748b"
                                }
                                Text {
                                    id: statusText
                                    text: window.lastMessage
                                    font.pixelSize: 13
                                    font.bold: true
                                    color: "#38bdf8"
                                }
                            }
                        }
                    }
                }
            }
        }

        // Bottom Footer Bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 36
            color: "#12141c"

            Rectangle {
                anchors.top: parent.top
                width: parent.width
                height: 1
                color: "#1e2230"
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 20
                anchors.rightMargin: 20

                Text {
                    text: "Offline-First Image Toolbox • Pure Python Engine"
                    font.pixelSize: 12
                    color: "#64748b"
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: "Ready for Phase 1 (Application Shell)"
                    font.pixelSize: 12
                    color: "#64748b"
                }
            }
        }
    }

    // Toast Notification Banner Component
    Rectangle {
        id: toastBanner
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 52
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
