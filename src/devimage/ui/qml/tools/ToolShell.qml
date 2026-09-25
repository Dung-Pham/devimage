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
                    source: toolShell.toolId === "resize" ? "ResizeTool.qml" : (toolShell.toolId === "compress" ? "CompressTool.qml" : (toolShell.toolId === "convert" ? "ConvertTool.qml" : ""))
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

                // Action Button
                Button {
                    id: processBtn
                    Layout.fillWidth: true
                    height: 42

                    property bool isBusy: (toolShell.toolId === "resize" && typeof resizeController !== "undefined" && resizeController && resizeController.isProcessing) || (toolShell.toolId === "compress" && typeof compressController !== "undefined" && compressController && compressController.isProcessing) || (toolShell.toolId === "convert" && typeof convertController !== "undefined" && convertController && convertController.isProcessing)

                    enabled: toolShell.currentImagePath.length > 0 && !isBusy
                    text: isBusy ? "Processing..." : ("Execute " + toolShell.toolTitle)

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

                // Top Toolbar: Clear / Change Image
                Button {
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.margins: 16
                    text: "Change Image"
                    font.pixelSize: 12

                    contentItem: Text { text: "Change Image"; color: "#cbd5e1"; font.pixelSize: 12 }
                    background: Rectangle {
                        implicitWidth: 100
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
