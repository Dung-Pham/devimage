import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: errorDlg
    anchors.centerIn: parent
    width: Math.min(parent ? parent.width - 48 : 500, 520)
    modal: true
    title: ""
    padding: 0

    property string errTitle: ""
    property string errDesc: ""
    property string errCause: ""
    property string errAction: ""
    property string errDetails: ""

    background: Rectangle {
        color: "#161922"
        radius: 12
        border.color: "#ef4444"
        border.width: 1.5
    }

    contentItem: ColumnLayout {
        spacing: 0

        // Header
        Rectangle {
            Layout.fillWidth: true
            height: 52
            color: "#221318"
            radius: 12

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 20
                anchors.rightMargin: 16
                spacing: 12

                Text { text: "⚠️"; font.pixelSize: 18 }

                Text {
                    text: errorDlg.errTitle || "Application Error"
                    font.pixelSize: 16
                    font.bold: true
                    color: "#f87171"
                    Layout.fillWidth: true
                }

                Button {
                    text: "✕"
                    font.pixelSize: 12
                    contentItem: Text { text: "✕"; color: "#94a3b8"; horizontalAlignment: Text.AlignHCenter }
                    background: Rectangle { implicitWidth: 24; implicitHeight: 24; radius: 12; color: "transparent" }
                    onClicked: errorDlg.close()
                }
            }
        }

        // Body Content
        ColumnLayout {
            Layout.fillWidth: true
            Layout.margins: 20
            spacing: 16

            Text {
                text: errorDlg.errDesc
                font.pixelSize: 14
                color: "#f8fafc"
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                lineHeight: 1.4
            }

            // Possible Cause Card
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: causeCol.implicitHeight + 20
                radius: 8
                color: "#1a1e2a"
                border.color: "#2e3549"

                ColumnLayout {
                    id: causeCol
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 4

                    Text {
                        text: "Possible Cause:"
                        font.bold: true
                        font.pixelSize: 12
                        color: "#94a3b8"
                    }
                    Text {
                        text: errorDlg.errCause || "An unexpected system or runtime state occurred."
                        font.pixelSize: 13
                        color: "#cbd5e1"
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }

            // Suggested Action Card
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: actionCol.implicitHeight + 20
                radius: 8
                color: "#082f49"
                border.color: "#0284c7"

                ColumnLayout {
                    id: actionCol
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 4

                    Text {
                        text: "Suggested Action:"
                        font.bold: true
                        font.pixelSize: 12
                        color: "#38bdf8"
                    }
                    Text {
                        text: errorDlg.errAction || "Retry the operation or select a different image file."
                        font.pixelSize: 13
                        color: "#e0f2fe"
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }

            // Bottom action buttons
            RowLayout {
                Layout.fillWidth: true
                Layout.topMargin: 8

                Item { Layout.fillWidth: true }

                Button {
                    text: "Dismiss"
                    font.bold: true
                    font.pixelSize: 13
                    contentItem: Text { text: "Dismiss"; font.bold: true; color: "#ffffff"; horizontalAlignment: Text.AlignHCenter }
                    background: Rectangle { implicitWidth: 90; implicitHeight: 36; radius: 6; color: "#475569" }
                    onClicked: errorDlg.close()
                }
            }
        }
    }

    function openError(title, description, cause, action, details) {
        errTitle = title
        errDesc = description
        errCause = cause
        errAction = action
        errDetails = details || ""
        open()
    }
}
