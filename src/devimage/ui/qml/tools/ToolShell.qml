import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Rectangle {
    id: toolShell
    color: "#0f1117"

    property string toolId: ""
    property string toolTitle: "Tool Workspace"
    property string toolDescription: "Configure parameters on the left and preview result on the right."
    property string currentImagePath: ""
    readonly property bool hasImage: currentImagePath.length > 0
    property alias zoomLevel: previewCanvas.zoomLevel

    signal backRequested()
    signal actionTriggered()

    function resetView() {
        if (previewCanvas) {
            previewCanvas.resetZoom()
        }
    }

    function fitToView() {
        if (previewCanvas) {
            previewCanvas.fitToView()
        }
    }

    onCurrentImagePathChanged: {
        if (toolShell.currentImagePath) {
            if (toolShell.toolId === "resize" && typeof resizeController !== "undefined" && resizeController) {
                resizeController.loadImage(toolShell.currentImagePath)
            } else if (toolShell.toolId === "compress" && typeof compressController !== "undefined" && compressController) {
                compressController.loadImage(toolShell.currentImagePath)
            } else if (toolShell.toolId === "convert" && typeof convertController !== "undefined" && convertController) {
                convertController.loadImage(toolShell.currentImagePath)
            } else if (toolShell.toolId === "crop" && typeof cropController !== "undefined" && cropController) {
                cropController.loadImage(toolShell.currentImagePath)
            } else if (toolShell.toolId === "inspector" && typeof inspectorController !== "undefined" && inspectorController) {
                inspectorController.loadImage(toolShell.currentImagePath)
            } else if (toolShell.toolId === "color_picker" && typeof colorPickerController !== "undefined" && colorPickerController) {
                colorPickerController.loadImage(toolShell.currentImagePath)
            }
        }
    }

    onToolIdChanged: {
        if (toolShell.currentImagePath) {
            if (toolShell.toolId === "resize" && typeof resizeController !== "undefined" && resizeController) {
                resizeController.loadImage(toolShell.currentImagePath)
            } else if (toolShell.toolId === "compress" && typeof compressController !== "undefined" && compressController) {
                compressController.loadImage(toolShell.currentImagePath)
            } else if (toolShell.toolId === "convert" && typeof convertController !== "undefined" && convertController) {
                convertController.loadImage(toolShell.currentImagePath)
            } else if (toolShell.toolId === "crop" && typeof cropController !== "undefined" && cropController) {
                cropController.loadImage(toolShell.currentImagePath)
            } else if (toolShell.toolId === "inspector" && typeof inspectorController !== "undefined" && inspectorController) {
                inspectorController.loadImage(toolShell.currentImagePath)
            } else if (toolShell.toolId === "color_picker" && typeof colorPickerController !== "undefined" && colorPickerController) {
                colorPickerController.loadImage(toolShell.currentImagePath)
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // Left Options / Parameters Panel
        Rectangle {
            Layout.preferredWidth: 320
            Layout.fillHeight: true
            color: "#141720"

            Rectangle {
                anchors.right: parent.right
                width: 1
                height: parent.height
                color: "#222736"
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16

                // Tool Header
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 6

                    Text {
                        text: toolShell.toolTitle
                        font.pixelSize: 18
                        font.bold: true
                        color: "#f8fafc"
                    }

                    Text {
                        text: toolShell.toolDescription
                        font.pixelSize: 12
                        color: "#94a3b8"
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: "#222736" }

                // Tool-specific options loader
                Loader {
                    id: toolOptionsLoader
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    source: toolShell.toolId === "resize" ? "ResizeTool.qml" : (toolShell.toolId === "compress" ? "CompressTool.qml" : (toolShell.toolId === "convert" ? "ConvertTool.qml" : (toolShell.toolId === "crop" ? "CropTool.qml" : (toolShell.toolId === "inspector" ? "InspectorTool.qml" : (toolShell.toolId === "color_picker" ? "ColorPickerTool.qml" : (toolShell.toolId === "rename" ? "RenameTool.qml" : (toolShell.toolId === "copy_path" ? "CopyPathTool.qml" : "")))))))
                    visible: source !== ""
                }

                // Placeholder container for generic/unimplemented tools
                ColumnLayout {
                    id: optionsPlaceholder
                    Layout.fillWidth: true
                    spacing: 12
                    visible: toolOptionsLoader.source === ""

                    Text {
                        text: "Options & Parameters"
                        font.pixelSize: 13
                        font.bold: true
                        color: "#cbd5e1"
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 90
                        radius: 8
                        color: "#1a1e2a"
                        border.color: "#262b3a"

                        Text {
                            anchors.centerIn: parent
                            text: toolShell.currentImagePath ? "Ready to process image." : "Select an image to activate options."
                            font.pixelSize: 12
                            color: "#64748b"
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                }

                Item {
                    Layout.fillHeight: true
                    visible: toolOptionsLoader.source === ""
                }

                // Action Button (hidden for read-only inspector, color_picker, and copy_path tools)
                Button {
                    id: processBtn
                    Layout.fillWidth: true
                    height: 42
                    visible: toolShell.toolId !== "inspector" && toolShell.toolId !== "color_picker" && toolShell.toolId !== "copy_path"

                    property bool isBusy: (toolShell.toolId === "resize" && typeof resizeController !== "undefined" && resizeController && resizeController.isProcessing) || (toolShell.toolId === "compress" && typeof compressController !== "undefined" && compressController && compressController.isProcessing) || (toolShell.toolId === "convert" && typeof convertController !== "undefined" && convertController && convertController.isProcessing) || (toolShell.toolId === "crop" && typeof cropController !== "undefined" && cropController && cropController.isProcessing) || (toolShell.toolId === "rename" && typeof renameController !== "undefined" && renameController && renameController.isProcessing)

                    enabled: toolShell.toolId === "rename" ? (typeof renameController !== "undefined" && renameController && renameController.hasFiles && !renameController.hasCollisions && !isBusy) : (toolShell.currentImagePath.length > 0 && !isBusy)
                    text: isBusy ? "Processing..." : (toolShell.toolId === "rename" ? ("Rename " + (typeof renameController !== "undefined" && renameController ? renameController.fileCount : 0) + " Files") : ("Execute " + toolShell.toolTitle))

                    contentItem: Text {
                        text: processBtn.text
                        font.bold: true
                        font.pixelSize: 13
                        color: processBtn.enabled ? "#ffffff" : "#64748b"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        radius: 8
                        color: processBtn.enabled ? (processBtn.down ? "#4338ca" : (processBtn.hovered ? "#4f46e5" : "#6366f1")) : "#1e2230"
                    }

                    onClicked: {
                        if (toolShell.toolId === "resize" && typeof resizeController !== "undefined" && resizeController) {
                            resizeController.executeResize()
                        } else if (toolShell.toolId === "compress" && typeof compressController !== "undefined" && compressController) {
                            compressController.executeCompress()
                        } else if (toolShell.toolId === "convert" && typeof convertController !== "undefined" && convertController) {
                            convertController.executeConvert()
                        } else if (toolShell.toolId === "crop" && typeof cropController !== "undefined" && cropController) {
                            cropController.executeCrop()
                        } else if (toolShell.toolId === "rename" && typeof renameController !== "undefined" && renameController) {
                            renameController.executeBatchRename()
                        } else {
                            if (backend) {
                                backend.signals.showToast(
                                    "success",
                                    toolShell.toolTitle,
                                    "Processing pipeline triggered",
                                    2500
                                )
                            }
                        }
                        toolShell.actionTriggered()
                    }
                }
            }
        }

        // Center / Main Workspace Canvas
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            // Dedicated Batch Rename Workspace
            Loader {
                id: renameWorkspaceLoader
                anchors.fill: parent
                active: toolShell.toolId === "rename"
                visible: active
                source: "../components/BatchRenameWorkspace.qml"
            }

            // Regular Image Workspace for other tools
            Item {
                anchors.fill: parent
                visible: toolShell.toolId !== "rename"

                // State A: No image loaded -> DropZone
                DropZone {
                    anchors.centerIn: parent
                    visible: !toolShell.currentImagePath
                    onFileDropped: function(path) {
                        toolShell.currentImagePath = backend ? backend.urlToPath(path) : path
                    }
                }

                // State B: Image loaded -> Interactive Preview
                Item {
                    anchors.fill: parent
                    visible: toolShell.currentImagePath.length > 0

                ImagePreview {
                    id: previewCanvas
                    anchors.fill: parent
                    imageSource: toolShell.currentImagePath
                }

                CropOverlay {
                    id: cropOverlay
                    anchors.fill: parent
                    visible: toolShell.toolId === "crop"
                    imgX: previewCanvas.imgDisplayX
                    imgY: previewCanvas.imgDisplayY
                    imgW: previewCanvas.imgDisplayWidth
                    imgH: previewCanvas.imgDisplayHeight
                }

                ColorPickerOverlay {
                    id: colorPickerOverlay
                    anchors.fill: parent
                    visible: toolShell.toolId === "color_picker"
                    imgX: previewCanvas.imgDisplayX
                    imgY: previewCanvas.imgDisplayY
                    imgW: previewCanvas.imgDisplayWidth
                    imgH: previewCanvas.imgDisplayHeight
                    origW: previewCanvas.originalWidth
                    origH: previewCanvas.originalHeight
                }

                // Top Toolbar: Image Info Badge & Change Image Button
                RowLayout {
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: 16
                    spacing: 12

                    // File info badge
                    Rectangle {
                        height: 32
                        radius: 6
                        color: "#181b24"
                        border.color: "#2e3549"
                        implicitWidth: fileInfoRow.implicitWidth + 24

                        RowLayout {
                            id: fileInfoRow
                            anchors.centerIn: parent
                            spacing: 8

                            Text {
                                text: "🖼"
                                font.pixelSize: 12
                            }

                            Text {
                                text: {
                                    if (!toolShell.currentImagePath) return ""
                                    var parts = toolShell.currentImagePath.split(/[\\/]/)
                                    return parts[parts.length - 1]
                                }
                                font.pixelSize: 12
                                font.bold: true
                                color: "#f8fafc"
                                elide: Text.ElideMiddle
                                Layout.maximumWidth: 320
                            }

                            Rectangle {
                                width: 1
                                height: 14
                                color: "#2e3549"
                                visible: previewCanvas.originalWidth > 0
                            }

                            Text {
                                text: previewCanvas.originalWidth + " × " + previewCanvas.originalHeight + " px"
                                font.pixelSize: 11
                                color: "#38bdf8"
                                visible: previewCanvas.originalWidth > 0
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    Button {
                        text: "Change Image"
                        font.pixelSize: 12

                        contentItem: Text {
                            text: "Change Image"
                            color: "#cbd5e1"
                            font.pixelSize: 12
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            implicitWidth: 105
                            implicitHeight: 32
                            radius: 6
                            color: "#1c202c"
                            border.color: "#333b4f"
                        }

                        onClicked: toolShell.currentImagePath = ""
                    }
                }
            }
        }
    }
}
}
