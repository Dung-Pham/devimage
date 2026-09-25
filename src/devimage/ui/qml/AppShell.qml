import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "common"

Rectangle {
    id: shell
    color: "#0f1117"

    // Navigation state
    property string currentRoute: "home"
    property string activeToolId: ""
    property string activeToolTitle: ""

    signal navigateRequested(string route, string toolId, string toolTitle)

    function navigateToHome() {
        currentRoute = "home"
        activeToolId = ""
        activeToolTitle = ""
        if (backend) {
            backend.signals.navigate("home")
        }
    }

    function navigateToTool(toolId, toolTitle) {
        activeToolId = toolId
        activeToolTitle = toolTitle
        currentRoute = "tool"
        if (backend) {
            backend.signals.selectTool(toolId)
        }
    }

    // Connect to external Python signals
    Connections {
        target: backend ? backend.signals : null

        function onToolActivated(toolId) {
            if (shell.activeToolId !== toolId) {
                shell.activeToolId = toolId
                shell.currentRoute = "tool"
            }
        }

        function onNavigated(route) {
            if (route === "home") {
                shell.navigateToHome()
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 1. Top Navigation Header
        Header {
            Layout.fillWidth: true
            currentRoute: shell.currentRoute
            activeToolTitle: shell.activeToolTitle
            onBackClicked: shell.navigateToHome()
            onSettingsClicked: {
                if (backend) {
                    backend.signals.showToast("info", "Settings", "Settings preferences dialog", 2000)
                }
            }
        }

        // 2. Central Dynamic Workspace Area
        Item {
            id: contentContainer
            Layout.fillWidth: true
            Layout.fillHeight: true

            // Active view container
            StackLayout {
                id: viewStack
                anchors.fill: parent
                currentIndex: shell.currentRoute === "home" ? 0 : 1

                // View 0: Home view container
                Item {
                    id: homeViewPage
                    // Will host Home.qml grid in TASK-P1-02
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 20
                        width: Math.min(parent.width - 48, 680)

                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: homeCardContent.implicitHeight + 40
                            radius: 12
                            color: "#161922"
                            border.color: "#262b3a"

                            ColumnLayout {
                                id: homeCardContent
                                anchors.fill: parent
                                anchors.margins: 24
                                spacing: 16

                                RowLayout {
                                    spacing: 12
                                    Rectangle {
                                        width: 12
                                        height: 12
                                        radius: 6
                                        color: "#10b981"
                                    }
                                    Text {
                                        text: "DevImage Application Shell Active"
                                        font.pixelSize: 18
                                        font.bold: true
                                        color: "#f8fafc"
                                    }
                                }

                                Text {
                                    text: "Modern desktop image toolbox designed for developers. Select any tool below to launch its workspace."
                                    font.pixelSize: 14
                                    color: "#94a3b8"
                                    wrapMode: Text.WordWrap
                                    Layout.fillWidth: true
                                    lineHeight: 1.4
                                }

                                Rectangle { Layout.fillWidth: true; height: 1; color: "#262b3a" }

                                // Quick test buttons to verify navigation
                                RowLayout {
                                    spacing: 12
                                    Button {
                                        text: "Open Resize Tool"
                                        onClicked: shell.navigateToTool("resize", "Resize Image")
                                    }
                                    Button {
                                        text: "Open Inspector"
                                        onClicked: shell.navigateToTool("inspector", "Image Inspector")
                                    }
                                }
                            }
                        }
                    }
                }

                // View 1: Active Tool view container
                Item {
                    id: toolViewPage
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 16

                        Text {
                            text: "Active Tool: " + shell.activeToolTitle + " (" + shell.activeToolId + ")"
                            font.pixelSize: 20
                            font.bold: true
                            color: "#f8fafc"
                            Layout.alignment: Qt.AlignHCenter
                        }

                        Text {
                            text: "Tool workspace and preview container loaded. Click 'Home' to return."
                            font.pixelSize: 14
                            color: "#94a3b8"
                            Layout.alignment: Qt.AlignHCenter
                        }

                        Button {
                            text: "← Return to Home"
                            Layout.alignment: Qt.AlignHCenter
                            onClicked: shell.navigateToHome()
                        }
                    }
                }
            }
        }

        // 3. Bottom Footer
        Footer {
            Layout.fillWidth: true
        }
    }
}
