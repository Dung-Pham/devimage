import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: colorPickerRoot
    clip: true
    ScrollBar.vertical.policy: ScrollBar.AsNeeded
    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

    ColumnLayout {
        width: parent.width
        spacing: 16

        // 1. Primary Sample Swatch Card
        Rectangle {
            Layout.fillWidth: true
            height: 100
            radius: 10
            color: colorPickerController ? colorPickerController.currentHex : "#3b82f6"
            border.color: "#333b4f"
            border.width: 1

            // Subtle inner glow / checkerboard corner for alpha
            Rectangle {
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.margins: 10
                height: 24
                radius: 6
                color: "#181b24cc"
                implicitWidth: coordText.implicitWidth + 16

                Text {
                    id: coordText
                    anchors.centerIn: parent
                    text: colorPickerController ? ("X: " + colorPickerController.coordX + "  Y: " + colorPickerController.coordY) : "X: 0 Y: 0"
                    font.pixelSize: 11
                    font.bold: true
                    color: "#f8fafc"
                }
            }

            ColumnLayout {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.margins: 14
                spacing: 2

                Text {
                    text: colorPickerController ? colorPickerController.currentHex : "#3B82F6"
                    font.pixelSize: 22
                    font.bold: true
                    color: colorPickerController ? colorPickerController.contrastText : "#ffffff"
                }

                Text {
                    text: colorPickerController ? colorPickerController.currentRgb : "rgb(59, 130, 246)"
                    font.pixelSize: 12
                    color: colorPickerController ? colorPickerController.contrastText : "#ffffff"
                    opacity: 0.85
                }
            }
        }

        // 2. Color Formats & Quick Copy Actions
        Text {
            text: "FORMATS & VALUES"
            font.pixelSize: 11
            font.bold: true
            color: "#64748b"
            font.letterSpacing: 1.0
        }

        // Format Card helper component
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            // HEX Row
            Rectangle {
                Layout.fillWidth: true
                height: 40
                radius: 8
                color: "#181b24"
                border.color: "#262b3a"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 8

                    Text {
                        text: "HEX"
                        font.pixelSize: 11
                        font.bold: true
                        color: "#94a3b8"
                        Layout.preferredWidth: 36
                    }

                    Text {
                        text: colorPickerController ? colorPickerController.currentHex : "#3B82F6"
                        font.pixelSize: 12
                        font.family: "monospace"
                        color: "#f8fafc"
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    Button {
                        text: "Copy"
                        Layout.preferredWidth: 50
                        Layout.preferredHeight: 26
                        contentItem: Text { text: "Copy"; font.pixelSize: 11; color: "#38bdf8"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        background: Rectangle { radius: 4; color: parent.hovered ? "#222736" : "transparent"; border.color: "#333b4f" }
                        onClicked: if (colorPickerController) colorPickerController.copyHex()
                    }
                }
            }

            // RGB Row
            Rectangle {
                Layout.fillWidth: true
                height: 40
                radius: 8
                color: "#181b24"
                border.color: "#262b3a"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 8

                    Text {
                        text: "RGB"
                        font.pixelSize: 11
                        font.bold: true
                        color: "#94a3b8"
                        Layout.preferredWidth: 36
                    }

                    Text {
                        text: colorPickerController ? colorPickerController.currentRgb : "rgb(59, 130, 246)"
                        font.pixelSize: 12
                        font.family: "monospace"
                        color: "#f8fafc"
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    Button {
                        text: "Copy"
                        Layout.preferredWidth: 50
                        Layout.preferredHeight: 26
                        contentItem: Text { text: "Copy"; font.pixelSize: 11; color: "#38bdf8"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        background: Rectangle { radius: 4; color: parent.hovered ? "#222736" : "transparent"; border.color: "#333b4f" }
                        onClicked: if (colorPickerController) colorPickerController.copyRgb()
                    }
                }
            }

            // HSL Row
            Rectangle {
                Layout.fillWidth: true
                height: 40
                radius: 8
                color: "#181b24"
                border.color: "#262b3a"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 8

                    Text {
                        text: "HSL"
                        font.pixelSize: 11
                        font.bold: true
                        color: "#94a3b8"
                        Layout.preferredWidth: 36
                    }

                    Text {
                        text: colorPickerController ? colorPickerController.currentHsl : "hsl(217, 91%, 60%)"
                        font.pixelSize: 12
                        font.family: "monospace"
                        color: "#f8fafc"
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    Button {
                        text: "Copy"
                        Layout.preferredWidth: 50
                        Layout.preferredHeight: 26
                        contentItem: Text { text: "Copy"; font.pixelSize: 11; color: "#38bdf8"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        background: Rectangle { radius: 4; color: parent.hovered ? "#222736" : "transparent"; border.color: "#333b4f" }
                        onClicked: if (colorPickerController) colorPickerController.copyHsl()
                    }
                }
            }

            // CSS Variable Row
            Rectangle {
                Layout.fillWidth: true
                height: 40
                radius: 8
                color: "#181b24"
                border.color: "#262b3a"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 8

                    Text {
                        text: "CSS"
                        font.pixelSize: 11
                        font.bold: true
                        color: "#94a3b8"
                        Layout.preferredWidth: 36
                    }

                    Text {
                        text: colorPickerController ? colorPickerController.currentCssVar : "--color-sampled: #3B82F6;"
                        font.pixelSize: 12
                        font.family: "monospace"
                        color: "#f8fafc"
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    Button {
                        text: "Copy"
                        Layout.preferredWidth: 50
                        Layout.preferredHeight: 26
                        contentItem: Text { text: "Copy"; font.pixelSize: 11; color: "#38bdf8"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        background: Rectangle { radius: 4; color: parent.hovered ? "#222736" : "transparent"; border.color: "#333b4f" }
                        onClicked: if (colorPickerController) colorPickerController.copyCssVar()
                    }
                }
            }
        }

        // 3. Channel breakdown bars
        Text {
            text: "CHANNEL VALUES"
            font.pixelSize: 11
            font.bold: true
            color: "#64748b"
            font.letterSpacing: 1.0
            Layout.topMargin: 4
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            // R
            Rectangle {
                Layout.fillWidth: true
                height: 34
                radius: 6
                color: "#261517"
                border.color: "#5c1d24"
                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 0
                    Text { text: "R"; font.pixelSize: 9; font.bold: true; color: "#f87171"; horizontalAlignment: Text.AlignHCenter }
                    Text { text: colorPickerController ? colorPickerController.r.toString() : "0"; font.pixelSize: 12; font.bold: true; color: "#ffffff"; horizontalAlignment: Text.AlignHCenter }
                }
            }

            // G
            Rectangle {
                Layout.fillWidth: true
                height: 34
                radius: 6
                color: "#13231b"
                border.color: "#166534"
                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 0
                    Text { text: "G"; font.pixelSize: 9; font.bold: true; color: "#4ade80"; horizontalAlignment: Text.AlignHCenter }
                    Text { text: colorPickerController ? colorPickerController.g.toString() : "0"; font.pixelSize: 12; font.bold: true; color: "#ffffff"; horizontalAlignment: Text.AlignHCenter }
                }
            }

            // B
            Rectangle {
                Layout.fillWidth: true
                height: 34
                radius: 6
                color: "#141c2e"
                border.color: "#1e3a8a"
                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 0
                    Text { text: "B"; font.pixelSize: 9; font.bold: true; color: "#60a5fa"; horizontalAlignment: Text.AlignHCenter }
                    Text { text: colorPickerController ? colorPickerController.b.toString() : "0"; font.pixelSize: 12; font.bold: true; color: "#ffffff"; horizontalAlignment: Text.AlignHCenter }
                }
            }

            // A
            Rectangle {
                Layout.fillWidth: true
                height: 34
                radius: 6
                color: "#1c192b"
                border.color: "#4c1d95"
                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 0
                    Text { text: "A"; font.pixelSize: 9; font.bold: true; color: "#c084fc"; horizontalAlignment: Text.AlignHCenter }
                    Text { text: colorPickerController ? colorPickerController.a.toString() : "255"; font.pixelSize: 12; font.bold: true; color: "#ffffff"; horizontalAlignment: Text.AlignHCenter }
                }
            }
        }

        // 4. Extracted Image Palette
        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 8

            Text {
                text: "DOMINANT PALETTE"
                font.pixelSize: 11
                font.bold: true
                color: "#64748b"
                font.letterSpacing: 1.0
                Layout.fillWidth: true
            }

            Button {
                text: "Copy CSS Palette"
                Layout.preferredHeight: 24
                visible: colorPickerController && colorPickerController.paletteColors.length > 0
                contentItem: Text { text: "Copy Palette"; font.pixelSize: 10; font.bold: true; color: "#818cf8"; verticalAlignment: Text.AlignVCenter }
                background: Rectangle { color: "transparent" }
                onClicked: if (colorPickerController) colorPickerController.copyPaletteCss()
            }
        }

        Flow {
            Layout.fillWidth: true
            spacing: 8
            visible: colorPickerController && colorPickerController.paletteColors.length > 0

            Repeater {
                model: colorPickerController ? colorPickerController.paletteColors : []

                Rectangle {
                    width: 32
                    height: 32
                    radius: 6
                    color: modelData.hex || "#3b82f6"
                    border.color: (colorPickerController && colorPickerController.currentHex === modelData.hex) ? "#ffffff" : "#333b4f"
                    border.width: (colorPickerController && colorPickerController.currentHex === modelData.hex) ? 2 : 1

                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (colorPickerController) {
                                colorPickerController.selectColor(modelData.hex)
                            }
                        }
                    }

                    ToolTip.visible: parent.border.width === 2 || (mouseAreaHover.containsMouse)
                    ToolTip.text: (modelData.hex || "") + " (" + (modelData.percentage || 0) + "%)"

                    MouseArea {
                        id: mouseAreaHover
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: if (colorPickerController) colorPickerController.selectColor(modelData.hex)
                    }
                }
            }
        }

        // 5. Export JSON Action
        Button {
            text: "Export Color JSON"
            Layout.fillWidth: true
            Layout.preferredHeight: 36
            Layout.topMargin: 8
            contentItem: Text {
                text: "📋  Copy Full Color JSON"
                font.pixelSize: 12
                font.bold: true
                color: "#f8fafc"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            background: Rectangle {
                radius: 6
                color: parent.hovered ? "#222736" : "#181b24"
                border.color: "#333b4f"
            }
            onClicked: if (colorPickerController) colorPickerController.copyJson()
        }

        // Extra padding at bottom
        Item {
            height: 24
        }
    }
}
