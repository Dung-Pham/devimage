import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: resizeTool
    Layout.fillWidth: true
    Layout.fillHeight: true
    clip: true
    contentWidth: availableWidth

    ColumnLayout {
        width: resizeTool.availableWidth
        spacing: 16

        // 1. Current / Original Dimensions Card
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
                        text: "ORIGINAL SIZE"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#64748b"
                    }
                    Text {
                        text: (typeof resizeController !== "undefined" && resizeController && resizeController.originalWidth > 0)
                              ? (resizeController.originalWidth + " × " + resizeController.originalHeight + " px")
                              : "No image loaded"
                        font.pixelSize: 13
                        font.bold: true
                        color: (typeof resizeController !== "undefined" && resizeController && resizeController.originalWidth > 0)
                               ? "#f8fafc" : "#64748b"
                    }
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: (typeof resizeController !== "undefined" && resizeController && resizeController.targetWidth > 0)
                          ? ("→ " + resizeController.targetWidth + " × " + resizeController.targetHeight)
                          : ""
                    font.pixelSize: 12
                    font.bold: true
                    color: "#818cf8"
                }
            }
        }

        // 2. Presets Selection
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: "Resolution Presets"
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
                    model: [1920, 1600, 1200, 1024, 768, 480]
                    delegate: Button {
                        id: presetBtn
                        Layout.fillWidth: true
                        height: 32

                        contentItem: Text {
                            text: modelData + "p"
                            font.pixelSize: 11
                            font.bold: true
                            color: presetBtn.hovered ? "#ffffff" : "#94a3b8"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        background: Rectangle {
                            radius: 6
                            color: presetBtn.down ? "#3730a3" : (presetBtn.hovered ? "#282e42" : "#1e2333")
                            border.color: presetBtn.hovered ? "#4f46e5" : "#2c3347"
                        }

                        onClicked: {
                            if (typeof resizeController !== "undefined" && resizeController) {
                                resizeController.applyPreset(modelData)
                            }
                        }
                    }
                }
            }
        }

        // 3. Custom Target Dimensions
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: "Target Dimensions"
                font.pixelSize: 12
                font.bold: true
                color: "#cbd5e1"
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                // Width Input
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4

                    Text { text: "Width (px)"; font.pixelSize: 11; color: "#94a3b8" }

                    TextField {
                        id: widthInput
                        Layout.fillWidth: true
                        height: 36
                        color: "#f8fafc"
                        font.pixelSize: 13
                        font.bold: true
                        validator: IntValidator { bottom: 1; top: 100000 }
                        text: (typeof resizeController !== "undefined" && resizeController && resizeController.targetWidth > 0)
                              ? String(resizeController.targetWidth) : ""

                        background: Rectangle {
                            radius: 6
                            color: "#1e2230"
                            border.color: widthInput.activeFocus ? "#6366f1" : "#333b4f"
                        }

                        onEditingFinished: {
                            var val = parseInt(text)
                            if (!isNaN(val) && val > 0 && typeof resizeController !== "undefined" && resizeController) {
                                resizeController.setTargetWidth(val)
                            }
                        }
                    }
                }

                // Aspect Ratio Lock Toggle Button
                Button {
                    id: aspectBtn
                    Layout.preferredWidth: 36
                    Layout.preferredHeight: 36
                    Layout.alignment: Qt.AlignBottom

                    property bool locked: typeof resizeController !== "undefined" && resizeController ? resizeController.keepAspect : true

                    contentItem: Text {
                        text: aspectBtn.locked ? "🔒" : "🔓"
                        font.pixelSize: 14
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        radius: 6
                        color: aspectBtn.locked ? "#312e81" : "#1e2230"
                        border.color: aspectBtn.locked ? "#6366f1" : "#333b4f"
                    }

                    onClicked: {
                        if (typeof resizeController !== "undefined" && resizeController) {
                            resizeController.setKeepAspect(!aspectBtn.locked)
                        }
                    }
                }

                // Height Input
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4

                    Text { text: "Height (px)"; font.pixelSize: 11; color: "#94a3b8" }

                    TextField {
                        id: heightInput
                        Layout.fillWidth: true
                        height: 36
                        color: "#f8fafc"
                        font.pixelSize: 13
                        font.bold: true
                        validator: IntValidator { bottom: 1; top: 100000 }
                        text: (typeof resizeController !== "undefined" && resizeController && resizeController.targetHeight > 0)
                              ? String(resizeController.targetHeight) : ""

                        background: Rectangle {
                            radius: 6
                            color: "#1e2230"
                            border.color: heightInput.activeFocus ? "#6366f1" : "#333b4f"
                        }

                        onEditingFinished: {
                            var val = parseInt(text)
                            if (!isNaN(val) && val > 0 && typeof resizeController !== "undefined" && resizeController) {
                                resizeController.setTargetHeight(val)
                            }
                        }
                    }
                }
            }
        }

        // 4. Scaling Mode
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: "Resize Mode"
                font.pixelSize: 12
                font.bold: true
                color: "#cbd5e1"
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                Repeater {
                    model: [
                        { id: "contain", label: "Fit (Contain)" },
                        { id: "cover", label: "Fill (Cover)" },
                        { id: "stretch", label: "Stretch" }
                    ]

                    delegate: Button {
                        id: modeBtn
                        Layout.fillWidth: true
                        height: 32

                        property bool isSelected: (typeof resizeController !== "undefined" && resizeController) ? resizeController.mode === modelData.id : (modelData.id === "contain")

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
                            color: isSelected ? "#4f46e5" : (modeBtn.hovered ? "#282e42" : "#1e2333")
                            border.color: isSelected ? "#6366f1" : "#2c3347"
                        }

                        onClicked: {
                            if (typeof resizeController !== "undefined" && resizeController) {
                                resizeController.setMode(modelData.id)
                            }
                        }
                    }
                }
            }
        }

        // 5. Constraints & Options
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            CheckBox {
                id: dontEnlargeCheck
                text: "Don't enlarge (prevent upscale)"
                checked: typeof resizeController !== "undefined" && resizeController ? resizeController.dontEnlarge : false

                contentItem: Text {
                    text: dontEnlargeCheck.text
                    font.pixelSize: 12
                    color: "#cbd5e1"
                    leftPadding: dontEnlargeCheck.indicator.width + 8
                    verticalAlignment: Text.AlignVCenter
                }

                onToggled: {
                    if (typeof resizeController !== "undefined" && resizeController) {
                        resizeController.setDontEnlarge(checked)
                    }
                }
            }
        }

        // 6. Processing State / Progress Indicator
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6
            visible: typeof resizeController !== "undefined" && resizeController && resizeController.isProcessing

            Text {
                text: typeof resizeController !== "undefined" && resizeController ? resizeController.statusMessage : ""
                font.pixelSize: 11
                color: "#818cf8"
            }

            ProgressBar {
                Layout.fillWidth: true
                height: 6
                from: 0.0
                to: 100.0
                value: typeof resizeController !== "undefined" && resizeController ? resizeController.progress : 0.0

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
