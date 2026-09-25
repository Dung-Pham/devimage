import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Item {
    id: batchWorkspace
    anchors.fill: parent

    readonly property var ctrl: (typeof renameController !== "undefined" && renameController) ? renameController : ((typeof backend !== "undefined" && backend && backend.renameController) ? backend.renameController : null)

    // Multi-file selection dialog
    FileDialog {
        id: fileDialog
        title: "Select Images to Batch Rename"
        fileMode: FileDialog.OpenFiles
        nameFilters: ["Image Files (*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.gif *.ico *.avif)", "All Files (*)"]
        onAccepted: {
            if (ctrl && selectedFiles.length > 0) {
                var paths = []
                for (var i = 0; i < selectedFiles.length; i++) {
                    var f = selectedFiles[i].toString()
                    paths.push(backend ? backend.urlToPath(f) : f)
                }
                ctrl.addFiles(paths)
            }
        }
    }

    // Drop area covering the entire workspace
    DropArea {
        id: workspaceDropArea
        anchors.fill: parent
        onDropped: function(drop) {
            if (drop.hasUrls && ctrl) {
                var droppedPaths = []
                for (var i = 0; i < drop.urls.length; i++) {
                    var rawUrl = drop.urls[i].toString()
                    var localPath = backend ? backend.urlToPath(rawUrl) : rawUrl
                    droppedPaths.push(localPath)
                }
                ctrl.addFiles(droppedPaths)
                drop.acceptProposedAction()
            }
        }
    }

    // -------------------------------------------------------------
    // State A: Empty Queue -> Prominent DropZone & Info
    // -------------------------------------------------------------
    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20
        visible: !ctrl || !ctrl.hasFiles

        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            width: 520
            height: 260
            radius: 12
            color: workspaceDropArea.containsDrag ? "#1e2238" : "#141721"
            border.color: workspaceDropArea.containsDrag ? "#6366f1" : "#262b3a"
            border.width: workspaceDropArea.containsDrag ? 2 : 1

            ColumnLayout {
                anchors.centerIn: parent
                spacing: 14

                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    width: 64
                    height: 64
                    radius: 32
                    color: "#1e2230"

                    Text {
                        anchors.centerIn: parent
                        text: "🏷️"
                        font.pixelSize: 28
                    }
                }

                ColumnLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 4

                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        text: "Drag and drop files to batch rename"
                        font.pixelSize: 15
                        font.bold: true
                        color: "#f8fafc"
                    }

                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        text: "Drop multiple images or click below to select files from disk"
                        font.pixelSize: 12
                        color: "#94a3b8"
                    }
                }

                Button {
                    id: browseBtn
                    Layout.alignment: Qt.AlignHCenter
                    height: 38
                    implicitWidth: 160
                    text: "Select Files..."
                    contentItem: Text {
                        text: browseBtn.text
                        color: "#ffffff"
                        font.pixelSize: 13
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        radius: 8
                        color: browseBtn.down ? "#4338ca" : (browseBtn.hovered ? "#4f46e5" : "#6366f1")
                    }
                    onClicked: fileDialog.open()
                }
            }
        }
    }

    // -------------------------------------------------------------
    // State B: Files Queued -> Full-Featured Batch Table
    // -------------------------------------------------------------
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 14
        visible: ctrl && ctrl.hasFiles

        // Workspace Header
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            ColumnLayout {
                spacing: 2
                Text {
                    text: "Batch Renaming Queue"
                    font.pixelSize: 16
                    font.bold: true
                    color: "#f8fafc"
                }
                Text {
                    text: ctrl ? ctrl.statusMessage : ""
                    font.pixelSize: 12
                    color: (ctrl && ctrl.hasCollisions) ? "#f87171" : "#38bdf8"
                }
            }

            Item { Layout.fillWidth: true }

            Button {
                id: addMoreBtn
                height: 32
                implicitWidth: 110
                text: "+ Add Files"
                contentItem: Text {
                    text: addMoreBtn.text
                    color: "#cbd5e1"
                    font.pixelSize: 12
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    radius: 6
                    color: addMoreBtn.hovered ? "#2a3042" : "#1a1e2a"
                    border.color: "#333b4f"
                }
                onClicked: fileDialog.open()
            }

            Button {
                id: clearBtn
                height: 32
                implicitWidth: 90
                text: "Clear All"
                contentItem: Text {
                    text: clearBtn.text
                    color: "#f87171"
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    radius: 6
                    color: clearBtn.hovered ? "#450a0a" : "#1a1e2a"
                    border.color: "#7f1d1d"
                }
                onClicked: {
                    if (ctrl) ctrl.clearFiles()
                }
            }
        }

        // Table Header
        Rectangle {
            Layout.fillWidth: true
            height: 32
            radius: 6
            color: "#181b24"
            border.color: "#222736"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 12

                Text {
                    text: "STATUS"
                    font.pixelSize: 10
                    font.bold: true
                    color: "#64748b"
                    Layout.preferredWidth: 60
                }

                Text {
                    text: "CURRENT FILENAME"
                    font.pixelSize: 10
                    font.bold: true
                    color: "#64748b"
                    Layout.fillWidth: true
                    Layout.preferredWidth: 200
                }

                Text {
                    text: ""
                    Layout.preferredWidth: 24
                }

                Text {
                    text: "NEW TARGET FILENAME"
                    font.pixelSize: 10
                    font.bold: true
                    color: "#64748b"
                    Layout.fillWidth: true
                    Layout.preferredWidth: 240
                }

                Text {
                    text: "RESOLUTION"
                    font.pixelSize: 10
                    font.bold: true
                    color: "#64748b"
                    Layout.preferredWidth: 90
                }

                Text {
                    text: "ACTION"
                    font.pixelSize: 10
                    font.bold: true
                    color: "#64748b"
                    Layout.preferredWidth: 50
                    horizontalAlignment: Text.AlignRight
                }
            }
        }

        // Table Scrollable Rows
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded

            ListView {
                id: fileListView
                width: parent.width
                model: ctrl ? ctrl.previews : []
                spacing: 6

                delegate: Rectangle {
                    width: fileListView.width
                    height: 48
                    radius: 8
                    color: modelData.status === "collision" ? "#3b1212" : (modelData.status === "exists" ? "#3d2208" : (rowMouse.containsMouse ? "#1c212e" : "#141721"))
                    border.color: modelData.status === "collision" ? "#ef4444" : (modelData.status === "exists" ? "#f59e0b" : "#222736")

                    MouseArea {
                        id: rowMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            // If user clicks row, set current image in workspace preview
                            toolShell.currentImagePath = modelData.source_path
                        }
                    }

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 16
                        anchors.rightMargin: 16
                        spacing: 12

                        // Status Badge
                        Rectangle {
                            Layout.preferredWidth: 60
                            height: 22
                            radius: 4
                            color: modelData.status === "ok" ? "#14532d" : (modelData.status === "collision" ? "#7f1d1d" : (modelData.status === "exists" ? "#78350f" : "#1e293b"))

                            Text {
                                anchors.centerIn: parent
                                text: modelData.status === "ok" ? "READY" : (modelData.status === "collision" ? "CONFLICT" : (modelData.status === "exists" ? "EXISTS" : "SAME"))
                                font.pixelSize: 9
                                font.bold: true
                                color: modelData.status === "ok" ? "#86efac" : (modelData.status === "collision" ? "#fca5a5" : (modelData.status === "exists" ? "#fde047" : "#94a3b8"))
                            }
                        }

                        // Current Name
                        Text {
                            text: modelData.source_name
                            font.pixelSize: 12
                            color: "#cbd5e1"
                            elide: Text.ElideMiddle
                            Layout.fillWidth: true
                            Layout.preferredWidth: 200
                        }

                        // Arrow
                        Text {
                            text: "→"
                            font.pixelSize: 14
                            font.bold: true
                            color: "#64748b"
                            Layout.preferredWidth: 24
                            horizontalAlignment: Text.AlignHCenter
                        }

                        // Target Name
                        Text {
                            text: modelData.target_name
                            font.pixelSize: 12
                            font.bold: true
                            color: modelData.status === "collision" ? "#fca5a5" : "#38bdf8"
                            elide: Text.ElideMiddle
                            Layout.fillWidth: true
                            Layout.preferredWidth: 240
                        }

                        // Resolution / Dimensions
                        Text {
                            text: (modelData.width > 0 && modelData.height > 0) ? (modelData.width + " × " + modelData.height) : "—"
                            font.pixelSize: 11
                            color: "#94a3b8"
                            Layout.preferredWidth: 90
                        }

                        // Action: Remove
                        Button {
                            Layout.preferredWidth: 50
                            height: 26
                            contentItem: Text {
                                text: "Remove"
                                font.pixelSize: 10
                                color: parent.hovered ? "#f87171" : "#64748b"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            background: Rectangle {
                                radius: 4
                                color: parent.hovered ? "#3b1212" : "transparent"
                                border.color: parent.hovered ? "#7f1d1d" : "transparent"
                            }
                            onClicked: {
                                if (ctrl) ctrl.removeFile(index)
                            }
                        }
                    }
                }
            }
        }
    }
}
