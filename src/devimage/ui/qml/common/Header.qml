import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    height: 60
    color: "#161922"

    property string currentRoute: "home"
    property string activeToolTitle: ""

    signal backClicked()
    signal settingsClicked()

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

        // Brand & Logo
        RowLayout {
            spacing: 12
            Rectangle {
                width: 34
                height: 34
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
                height: 22
                radius: 11
                color: "#1e293b"
                border.color: "#334155"
                Text {
                    anchors.centerIn: parent
                    text: "v" + (backend ? backend.appVersion : "0.1.0")
                    font.pixelSize: 11
                    font.bold: true
                    color: "#94a3b8"
                }
            }
        }

        // Breadcrumb & Back Navigation Button
        RowLayout {
            visible: root.currentRoute !== "home"
            spacing: 8

            Rectangle { width: 1; height: 24; color: "#2e3446"; Layout.leftMargin: 8; Layout.rightMargin: 8 }

            Button {
                id: backBtn
                text: "← Home"
                font.pixelSize: 13
                font.bold: true
                
                contentItem: Text {
                    text: backBtn.text
                    font: backBtn.font
                    color: backBtn.hovered ? "#ffffff" : "#94a3b8"
                    verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    implicitWidth: 80
                    implicitHeight: 32
                    radius: 6
                    color: backBtn.down ? "#2e3446" : (backBtn.hovered ? "#222736" : "transparent")
                    border.color: backBtn.hovered ? "#3b4259" : "transparent"
                }

                onClicked: root.backClicked()
            }

            Text {
                text: "/"
                color: "#64748b"
                font.pixelSize: 14
            }

            Text {
                text: root.activeToolTitle
                font.pixelSize: 14
                font.bold: true
                color: "#38bdf8"
            }
        }

        Item { Layout.fillWidth: true }

        // Settings Button
        Button {
            id: settingsBtn
            text: "⚙ Settings"
            font.pixelSize: 13
            
            contentItem: Text {
                text: settingsBtn.text
                font: settingsBtn.font
                color: settingsBtn.hovered ? "#ffffff" : "#cbd5e1"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            background: Rectangle {
                implicitWidth: 100
                implicitHeight: 34
                radius: 6
                color: settingsBtn.down ? "#333b4f" : (settingsBtn.hovered ? "#262b3a" : "#1c202c")
                border.color: settingsBtn.hovered ? "#475569" : "#2e3446"
            }

            onClicked: root.settingsClicked()
        }
    }
}
