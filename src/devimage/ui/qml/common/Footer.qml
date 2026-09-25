import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    height: 36
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

        RowLayout {
            spacing: 8
            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: "#10b981"
            }
            Text {
                text: "Offline-First Engine • Pure Python 3.14 + PySide6"
                font.pixelSize: 12
                color: "#64748b"
            }
        }

        Item { Layout.fillWidth: true }

        Text {
            text: "Fast • Local • Private"
            font.pixelSize: 12
            color: "#64748b"
        }
    }
}
