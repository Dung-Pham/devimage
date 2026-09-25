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
    signal settingsRequested()

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
            onSettingsClicked: shell.settingsRequested()
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
                Home {
                    id: homeView
                    onToolSelected: function(toolId, toolTitle) {
                        shell.navigateToTool(toolId, toolTitle)
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
