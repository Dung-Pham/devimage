import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: compressTool
    Layout.fillWidth: true
    Layout.fillHeight: true
    clip: true
    contentWidth: availableWidth

    ColumnLayout {
        width: compressTool.availableWidth
        spacing: 16

        // 1. Size Comparison Card
        Rectangle {
            Layout.fillWidth: true
            height: 72
            radius: 8
            color: "#1a1e2a"
            border.color: "#262b3a"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                // Original Size
                ColumnLayout {
                    spacing: 2
                    Text {
                        text: "ORIGINAL"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#64748b"
                    }
                    Text {
                        text: (typeof compressController !== "undefined" && compressController)
                              ? compressController.originalSizeText : "—"
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

                // Estimated Size
                ColumnLayout {
                    spacing: 2
                    Text {
                        text: "ESTIMATED"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#64748b"
                    }
                    Text {
                        text: (typeof compressController !== "undefined" && compressController)
                              ? compressController.estimatedSizeText : "—"
                        font.pixelSize: 14
                        font.bold: true
                        color: "#818cf8"
                    }
                }

                Item { Layout.fillWidth: true }

                // Reduction Badge
                Rectangle {
                    visible: typeof compressController !== "undefined" && compressController && compressController.estimatedReduction > 0
                    radius: 6
                    color: "#064e3b"
                    border.color: "#059669"
                    implicitWidth: reductionText.implicitWidth + 16
                    implicitHeight: 28

                    Text {
                        id: reductionText
                        anchors.centerIn: parent
                        text: (typeof compressController !== "undefined" && compressController)
                              ? ("-" + compressController.estimatedReduction + "%") : ""
                        font.pixelSize: 12
                        font.bold: true
                        color: "#34d399"
                    }
                }
            }
        }

        // 2. Quality Slider
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            RowLayout {
                Layout.fillWidth: true
                Text {
                    text: "Compression Quality"
                    font.pixelSize: 12
                    font.bold: true
                    color: "#cbd5e1"
                }
                Item { Layout.fillWidth: true }
                Text {
                    text: (typeof compressController !== "undefined" && compressController)
                          ? (compressController.quality + "%") : "80%"
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
                value: typeof compressController !== "undefined" && compressController ? compressController.quality : 80

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
                    if (typeof compressController !== "undefined" && compressController) {
                        compressController.setQuality(Math.round(value))
                    }
                }
            }
        }

        // 3. Target Output Format
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
                        { id: "original", label: "Original" },
                        { id: "webp", label: "WebP" },
                        { id: "jpeg", label: "JPEG" }
                    ]

                    delegate: Button {
                        id: fmtBtn
                        Layout.fillWidth: true
                        height: 32

                        property bool isSelected: (typeof compressController !== "undefined" && compressController)
                                                  ? compressController.targetFormat === modelData.id
                                                  : (modelData.id === "original")

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
                            color: isSelected ? "#4f46e5" : (fmtBtn.hovered ? "#282e42" : "#1e2333")
                            border.color: isSelected ? "#6366f1" : "#2c3347"
                        }

                        onClicked: {
                            if (typeof compressController !== "undefined" && compressController) {
                                compressController.setTargetFormat(modelData.id)
                            }
                        }
                    }
                }
            }
        }

        // 4. Advanced Toggles
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            CheckBox {
                id: stripCheck
                text: "Remove metadata / EXIF (save space)"
                checked: typeof compressController !== "undefined" && compressController ? compressController.stripMetadata : true

                contentItem: Text {
                    text: stripCheck.text
                    font.pixelSize: 12
                    color: "#cbd5e1"
                    leftPadding: stripCheck.indicator.width + 8
                    verticalAlignment: Text.AlignVCenter
                }

                onToggled: {
                    if (typeof compressController !== "undefined" && compressController) {
                        compressController.setStripMetadata(checked)
                    }
                }
            }

            CheckBox {
                id: quantizeCheck
                text: "Optimize PNG palette (quantize colors)"
                checked: typeof compressController !== "undefined" && compressController ? compressController.pngQuantize : false

                contentItem: Text {
                    text: quantizeCheck.text
                    font.pixelSize: 12
                    color: "#cbd5e1"
                    leftPadding: quantizeCheck.indicator.width + 8
                    verticalAlignment: Text.AlignVCenter
                }

                onToggled: {
                    if (typeof compressController !== "undefined" && compressController) {
                        compressController.setPngQuantize(checked)
                    }
                }
            }
        }

        // 5. Progress Indicator
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6
            visible: typeof compressController !== "undefined" && compressController && compressController.isProcessing

            Text {
                text: typeof compressController !== "undefined" && compressController ? compressController.statusMessage : ""
                font.pixelSize: 11
                color: "#818cf8"
            }

            ProgressBar {
                Layout.fillWidth: true
                height: 6
                from: 0.0
                to: 100.0
                value: typeof compressController !== "undefined" && compressController ? compressController.progress : 0.0

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
