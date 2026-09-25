import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: convertTool
    Layout.fillWidth: true
    Layout.fillHeight: true
    clip: true
    contentWidth: availableWidth

    ColumnLayout {
        width: convertTool.availableWidth
        spacing: 16

        // 1. Current / Target Format Overview Card
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
                        text: "SOURCE FORMAT"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#64748b"
                    }
                    Text {
                        text: (typeof convertController !== "undefined" && convertController && convertController.originalFormat)
                              ? convertController.originalFormat : "—"
                        font.pixelSize: 14
                        font.bold: true
                        color: "#f8fafc"
                    }
                }

                Text {
                    text: "→"
                    font.pixelSize: 16
                    color: "#475569"
                }

                ColumnLayout {
                    spacing: 2
                    Text {
                        text: "OUTPUT NAME"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#64748b"
                    }
                    Text {
                        text: (typeof convertController !== "undefined" && convertController && convertController.outputFilename)
                              ? convertController.outputFilename : "—"
                        font.pixelSize: 13
                        font.bold: true
                        color: "#818cf8"
                        elide: Text.ElideMiddle
                        Layout.maximumWidth: 160
                    }
                }
            }
        }

        // 2. Target Format Selection Chips
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: "Target Format"
                font.pixelSize: 12
                font.bold: true
                color: "#cbd5e1"
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                Repeater {
                    model: [
                        { id: "webp", label: "WebP", sub: "Modern & Small" },
                        { id: "png", label: "PNG", sub: "Lossless Alpha" },
                        { id: "jpeg", label: "JPEG", sub: "Universal" }
                    ]

                    delegate: Button {
                        id: fmtBtn
                        Layout.fillWidth: true
                        height: 48

                        property bool isSelected: (typeof convertController !== "undefined" && convertController)
                                                  ? convertController.targetFormat === modelData.id
                                                  : (modelData.id === "webp")

                        contentItem: ColumnLayout {
                            spacing: 2
                            Text {
                                text: modelData.label
                                font.pixelSize: 13
                                font.bold: true
                                color: isSelected ? "#ffffff" : "#cbd5e1"
                                Layout.alignment: Qt.AlignHCenter
                            }
                            Text {
                                text: modelData.sub
                                font.pixelSize: 10
                                color: isSelected ? "#c7d2fe" : "#64748b"
                                Layout.alignment: Qt.AlignHCenter
                            }
                        }

                        background: Rectangle {
                            radius: 8
                            color: isSelected ? "#4f46e5" : (fmtBtn.hovered ? "#282e42" : "#1e2333")
                            border.color: isSelected ? "#6366f1" : "#2c3347"
                        }

                        onClicked: {
                            if (typeof convertController !== "undefined" && convertController) {
                                convertController.setTargetFormat(modelData.id)
                            }
                        }
                    }
                }
            }
        }

        // 3. Quality Settings (for WebP and JPEG)
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6
            visible: typeof convertController !== "undefined" && convertController && convertController.targetFormat !== "png"

            RowLayout {
                Layout.fillWidth: true
                Text {
                    text: "Encoding Quality"
                    font.pixelSize: 12
                    font.bold: true
                    color: "#cbd5e1"
                }
                Item { Layout.fillWidth: true }
                Text {
                    text: (typeof convertController !== "undefined" && convertController)
                          ? (convertController.quality + "%") : "90%"
                    font.pixelSize: 12
                    font.bold: true
                    color: "#6366f1"
                }
            }

            Slider {
                id: qualitySlider
                Layout.fillWidth: true
                from: 1
                to: 100
                stepSize: 1
                value: typeof convertController !== "undefined" && convertController ? convertController.quality : 90

                background: Rectangle {
                    x: qualitySlider.leftPadding
                    y: qualitySlider.topPadding + qualitySlider.availableHeight / 2 - height / 2
                    implicitWidth: 200
                    implicitHeight: 6
                    width: qualitySlider.availableWidth
                    height: implicitHeight
                    radius: 3
                    color: "#1e2230"

                    Rectangle {
                        width: qualitySlider.visualPosition * parent.width
                        height: parent.height
                        color: "#6366f1"
                        radius: 3
                    }
                }

                handle: Rectangle {
                    x: qualitySlider.leftPadding + qualitySlider.visualPosition * (qualitySlider.availableWidth - width)
                    y: qualitySlider.topPadding + qualitySlider.availableHeight / 2 - height / 2
                    implicitWidth: 16
                    implicitHeight: 16
                    radius: 8
                    color: qualitySlider.pressed ? "#4338ca" : "#818cf8"
                    border.color: "#ffffff"
                    border.width: 1
                }

                onMoved: {
                    if (typeof convertController !== "undefined" && convertController) {
                        convertController.setQuality(Math.round(value))
                    }
                }
            }
        }

        // 4. Metadata Options
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            CheckBox {
                id: stripCheck
                text: "Remove metadata / EXIF"
                checked: typeof convertController !== "undefined" && convertController ? convertController.stripMetadata : false

                contentItem: Text {
                    text: stripCheck.text
                    font.pixelSize: 12
                    color: "#cbd5e1"
                    leftPadding: stripCheck.indicator.width + 8
                    verticalAlignment: Text.AlignVCenter
                }

                onToggled: {
                    if (typeof convertController !== "undefined" && convertController) {
                        convertController.setStripMetadata(checked)
                    }
                }
            }
        }

        // 5. Progress Indicator
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6
            visible: typeof convertController !== "undefined" && convertController && convertController.isProcessing

            Text {
                text: typeof convertController !== "undefined" && convertController ? convertController.statusMessage : ""
                font.pixelSize: 11
                color: "#818cf8"
            }

            ProgressBar {
                Layout.fillWidth: true
                height: 6
                from: 0.0
                to: 100.0
                value: typeof convertController !== "undefined" && convertController ? convertController.progress : 0.0

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
