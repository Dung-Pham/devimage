import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    height: 42
    radius: 8
    color: "#161922"
    border.color: searchField.activeFocus ? "#6366f1" : "#262b3a"
    border.width: searchField.activeFocus ? 2 : 1

    property alias text: searchField.text
    property alias placeholderText: searchField.placeholderText

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 14
        anchors.rightMargin: 10
        spacing: 10

        Text {
            text: "🔍"
            font.pixelSize: 14
            color: "#64748b"
        }

        TextField {
            id: searchField
            Layout.fillWidth: true
            placeholderText: "Search tools (e.g., resize, background, ocr)..."
            placeholderTextColor: "#64748b"
            color: "#f8fafc"
            font.pixelSize: 13
            background: Item {}
            selectByMouse: true
        }

        Button {
            visible: searchField.text.length > 0
            text: "✕"
            font.pixelSize: 11
            contentItem: Text {
                text: "✕"
                color: "#94a3b8"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            background: Rectangle {
                implicitWidth: 20
                implicitHeight: 20
                radius: 10
                color: "#222736"
            }
            onClicked: searchField.text = ""
        }
    }
}
