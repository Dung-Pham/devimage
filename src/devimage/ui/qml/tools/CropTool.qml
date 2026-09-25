import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: cropTool
    Layout.fillWidth: true
    Layout.fillHeight: true
    clip: true
    contentWidth: availableWidth

    ColumnLayout {
        width: cropTool.availableWidth
        spacing: 16

        // 1. Original Dimensions Card
        Rectangle {
            Layout.fillWidth: true
            height: 54
            radius: 8
            color: "#1a1e2a"
            border.color: "#262b3a"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12

                ColumnLayout {
                    spacing: 2
                    Text {
                        text: "ORIGINAL IMAGE"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#64748b"
                    }
                    Text {
                        text: (typeof cropController !== "undefined" && cropController && cropController.hasImage)
                              ? (cropController.originalWidth + " × " + cropController.originalHeight + " px")
                              : "No image loaded"
                        font.pixelSize: 13
                        font.bold: true
                        color: "#f8fafc"
                    }
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: (typeof cropController !== "undefined" && cropController && cropController.hasImage)
                          ? "Ready" : ""
                    font.pixelSize: 11
                    color: "#34d399"
                }
            }
        }

        // 2. Output Dimensions Card
        Rectangle {
            Layout.fillWidth: true
            height: 60
            radius: 8
            color: "#1a1e2a"
            border.color: "#262b3a"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                ColumnLayout {
                    spacing: 2
                    Text {
                        text: "CROPPED SIZE"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#64748b"
                    }
                    Text {
                        text: (typeof cropController !== "undefined" && cropController && cropController.hasImage)
                              ? (cropController.pixelCropWidth + " × " + cropController.pixelCropHeight + " px")
                              : "—"
                        font.pixelSize: 14
                        font.bold: true
                        color: "#f8fafc"
                    }
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: (typeof cropController !== "undefined" && cropController && cropController.rotation !== 0)
                          ? (cropController.rotation + "° Rotated") : ""
                    font.pixelSize: 11
                    font.bold: true
                    color: "#818cf8"
                }
            }
        }

        // 2. Aspect Ratio Presets
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: "Aspect Ratio"
                font.pixelSize: 12
                font.bold: true
                color: "#cbd5e1"
            }

            GridLayout {
                columns: 3
                Layout.fillWidth: true
                columnSpacing: 6
                rowSpacing: 6

                Repeater {
                    model: [
                        { id: "free", label: "Freeform" },
                        { id: "original", label: "Original" },
                        { id: "1:1", label: "1:1 Square" },
                        { id: "4:3", label: "4:3 Standard" },
                        { id: "3:4", label: "3:4 Portrait" },
                        { id: "16:9", label: "16:9 Wide" },
                        { id: "9:16", label: "9:16 Story" }
                    ]

                    delegate: Button {
                        id: aspectBtn
                        Layout.fillWidth: true
                        height: 32

                        property bool isSelected: (typeof cropController !== "undefined" && cropController)
                                                  ? cropController.aspectRatioMode === modelData.id
                                                  : (modelData.id === "free")

                        contentItem: Text {
                            text: modelData.label
                            font.pixelSize: 11
                            font.bold: isSelected
                            color: isSelected ? "#ffffff" : "#94a3b8"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        background: Rectangle {
                            radius: 6
                            color: isSelected ? "#4f46e5" : (aspectBtn.hovered ? "#282e42" : "#1e2333")
                            border.color: isSelected ? "#6366f1" : "#2c3347"
                        }

                        onClicked: {
                            if (typeof cropController !== "undefined" && cropController) {
                                cropController.setAspectRatioMode(modelData.id)
                            }
                        }
                    }
                }
            }
        }

        // 3. Transformation & Quick Actions
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: "Orientation & Alignment"
                font.pixelSize: 12
                font.bold: true
                color: "#cbd5e1"
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                Button {
                    Layout.fillWidth: true
                    height: 34
                    text: "⟲ Rotate CCW"

                    contentItem: Text {
                        text: "⟲ Rotate -90°"
                        font.pixelSize: 11
                        color: "#cbd5e1"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        radius: 6
                        color: "#1e2333"
                        border.color: "#2c3347"
                    }

                    onClicked: {
                        if (typeof cropController !== "undefined" && cropController) {
                            cropController.rotateCounterClockwise()
                        }
                    }
                }

                Button {
                    Layout.fillWidth: true
                    height: 34

                    contentItem: Text {
                        text: "⟳ Rotate +90°"
                        font.pixelSize: 11
                        color: "#cbd5e1"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        radius: 6
                        color: "#1e2333"
                        border.color: "#2c3347"
                    }

                    onClicked: {
                        if (typeof cropController !== "undefined" && cropController) {
                            cropController.rotateClockwise()
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                Button {
                    Layout.fillWidth: true
                    height: 34

                    contentItem: Text {
                        text: "🎯 Center Crop"
                        font.pixelSize: 11
                        color: "#cbd5e1"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        radius: 6
                        color: "#1e2333"
                        border.color: "#2c3347"
                    }

                    onClicked: {
                        if (typeof cropController !== "undefined" && cropController) {
                            cropController.centerCrop()
                        }
                    }
                }

                Button {
                    Layout.fillWidth: true
                    height: 34

                    contentItem: Text {
                        text: "↺ Reset Box"
                        font.pixelSize: 11
                        color: "#cbd5e1"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        radius: 6
                        color: "#1e2333"
                        border.color: "#2c3347"
                    }

                    onClicked: {
                        if (typeof cropController !== "undefined" && cropController) {
                            cropController.resetCrop()
                        }
                    }
                }
            }
        }

        // 4. Progress Indicator
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6
            visible: typeof cropController !== "undefined" && cropController && cropController.isProcessing

            Text {
                text: typeof cropController !== "undefined" && cropController ? cropController.statusMessage : ""
                font.pixelSize: 11
                color: "#818cf8"
            }

            ProgressBar {
                Layout.fillWidth: true
                height: 6
                from: 0.0
                to: 100.0
                value: typeof cropController !== "undefined" && cropController ? cropController.progress : 0.0

                background: Rectangle {
                    radius: 3
                    color: "#1e2230"
                }

                contentItem: Item {
                    Rectangle {
                        width: parent.width * (parent.parent.value / 100.0)
                        height: parent.height
                        radius: 3
                        color: "#6366f1"
                    }
                }
            }
        }
    }
}
