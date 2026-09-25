import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "common"
import "tools"

Rectangle {
    id: shell
    objectName: "appShell"
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

        function onFileSelected(filePath) {
            if (shell.currentRoute === "home") {
                shell.navigateToTool("resize", "Resize Image")
            }
            if (activeToolShell) {
                activeToolShell.currentImagePath = filePath
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
                    objectName: "homeView"
                    onToolSelected: function(toolId, toolTitle) {
                        shell.navigateToTool(toolId, toolTitle)
                    }
                }

                // View 1: Active Tool view container
                ToolShell {
                    id: activeToolShell
                    objectName: "activeToolShell"
                    toolId: shell.activeToolId
                    toolTitle: shell.activeToolTitle
                    onBackRequested: shell.navigateToHome()
                }
            }
        }

        // 3. Bottom Footer
        Footer {
            Layout.fillWidth: true
        }
    }
}
