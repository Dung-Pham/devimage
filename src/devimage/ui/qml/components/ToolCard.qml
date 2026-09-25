import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: card
    objectName: "toolCard"
    implicitWidth: 290
    implicitHeight: 96
    radius: 10
    color: mouseArea.containsMouse ? "#1c202c" : "#161922"
    border.color: mouseArea.containsMouse ? "#6366f1" : "#262b3a"
    border.width: mouseArea.containsMouse ? 1.5 : 1

    property string toolId: ""
    property string title: ""
    property string description: ""
    property string iconGlyph: "🛠"
    property string category: "image"
    property bool isAi: false

    signal clicked()

    Behavior on color { ColorAnimation { duration: 150 } }
    Behavior on border.color { ColorAnimation { duration: 150 } }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: card.clicked()
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 14

        // Icon Badge
        Rectangle {
            width: 44
            height: 44
            radius: 8
            color: card.isAi ? "#2e1065" : (mouseArea.containsMouse ? "#312e81" : "#1e2230")
            border.color: card.isAi ? "#9333ea" : (mouseArea.containsMouse ? "#4f46e5" : "#2e3446")

            Text {
                anchors.centerIn: parent
                text: card.iconGlyph
                font.pixelSize: 20
            }
        }

        // Title and description
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 4

            RowLayout {
                spacing: 8
                Text {
                    text: card.title
                    font.pixelSize: 15
                    font.bold: true
                    color: mouseArea.containsMouse ? "#ffffff" : "#f1f5f9"
                }

                Rectangle {
                    visible: card.isAi
                    width: 30
                    height: 16
                    radius: 4
                    color: "#581c87"
                    Text {
                        anchors.centerIn: parent
                        text: "AI"
                        font.pixelSize: 9
                        font.bold: true
                        color: "#d8b4fe"
                    }
                }
            }

            Text {
                text: card.description
                font.pixelSize: 12
                color: "#94a3b8"
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                maximumLineCount: 2
                elide: Text.ElideRight
            }
        }
    }
}
