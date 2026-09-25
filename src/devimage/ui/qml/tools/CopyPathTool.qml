import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: copyPathTool
    Layout.fillWidth: true
    Layout.fillHeight: true
    clip: true
    contentWidth: availableWidth
    ScrollBar.vertical.policy: ScrollBar.AsNeeded

    readonly property var ctrl: (typeof copyPathController !== "undefined" && copyPathController) ? copyPathController : ((typeof backend !== "undefined" && backend && backend.copyPathController) ? backend.copyPathController : null)

    // Listen to toolShell image changes
    Connections {
        target: toolShell
        function onCurrentImagePathChanged() {
            if (ctrl && toolShell.currentImagePath) {
                ctrl.loadImage(toolShell.currentImagePath)
            }
        }
    }

    Component.onCompleted: {
        if (ctrl && toolShell.currentImagePath) {
            ctrl.loadImage(toolShell.currentImagePath)
        }
    }

    ColumnLayout {
        width: copyPathTool.availableWidth
        spacing: 14

        // Placeholder when no image is loaded
        Rectangle {
            Layout.fillWidth: true
            height: 90
            radius: 8
            color: "#1a1e2a"
            border.color: "#262b3a"
            visible: !ctrl || !ctrl.hasImage

            Text {
                anchors.centerIn: parent
                text: "Select or drop an image\nto generate and copy developer path formats."
                font.pixelSize: 12
                color: "#64748b"
                horizontalAlignment: Text.AlignHCenter
            }
        }

        // Active Snippets View
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 12
            visible: ctrl && ctrl.hasImage

            // 1. Primary Actions Row
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Button {
                    id: explorerBtn
                    Layout.fillWidth: true
                    height: 34
                    text: "📂 Reveal in Explorer"
                    contentItem: Text {
                        text: explorerBtn.text
                        color: "#f8fafc"
                        font.pixelSize: 11
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        radius: 6
                        color: explorerBtn.hovered ? "#334155" : "#1e293b"
                        border.color: "#475569"
                    }
                    onClicked: {
                        if (ctrl) ctrl.revealInExplorer()
                    }
                }

                Button {
                    id: copyPosixBtn
                    Layout.fillWidth: true
                    height: 34
                    text: "🌐 Copy POSIX Path"
                    contentItem: Text {
                        text: copyPosixBtn.text
                        color: "#ffffff"
                        font.pixelSize: 11
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        radius: 6
                        color: copyPosixBtn.down ? "#4338ca" : (copyPosixBtn.hovered ? "#4f46e5" : "#6366f1")
                    }
                    onClicked: {
                        if (ctrl) ctrl.copySnippet("posix")
                    }
                }
            }

            // 2. Formatted Snippet Cards
            Repeater {
                model: ctrl ? ctrl.snippets : []

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: cardCol.implicitHeight + 20
                    radius: 8
                    color: snippetMouse.containsMouse ? "#1c212e" : "#141721"
                    border.color: snippetMouse.containsMouse ? "#4338ca" : "#222736"

                    MouseArea {
                        id: snippetMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (ctrl) ctrl.copyToClipboard(modelData.value, modelData.title)
                        }
                    }

                    ColumnLayout {
                        id: cardCol
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 6

                        // Header: Icon + Title + Description + Copy Button
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Text {
                                text: modelData.icon
                                font.pixelSize: 13
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 1

                                Text {
                                    text: modelData.title
                                    font.pixelSize: 11
                                    font.bold: true
                                    color: "#f8fafc"
                                }

                                Text {
                                    text: modelData.description
                                    font.pixelSize: 10
                                    color: "#64748b"
                                }
                            }

                            Button {
                                implicitWidth: 54
                                implicitHeight: 24
                                text: "Copy"
                                contentItem: Text {
                                    text: parent.text
                                    color: "#38bdf8"
                                    font.pixelSize: 10
                                    font.bold: true
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                background: Rectangle {
                                    radius: 4
                                    color: parent.hovered ? "#0369a1" : "#0c4a6e"
                                }
                                onClicked: {
                                    if (ctrl) ctrl.copyToClipboard(modelData.value, modelData.title)
                                }
                            }
                        }

                        // Code Box preview
                        Rectangle {
                            Layout.fillWidth: true
                            height: 28
                            radius: 4
                            color: "#0a0c10"
                            border.color: "#1e2230"

                            Text {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                anchors.rightMargin: 8
                                verticalAlignment: Text.AlignVCenter
                                text: modelData.value
                                font.pixelSize: 10
                                font.family: "monospace"
                                color: "#94a3b8"
                                elide: Text.ElideMiddle
                            }
                        }
                    }
                }
            }
        }
    }
}
