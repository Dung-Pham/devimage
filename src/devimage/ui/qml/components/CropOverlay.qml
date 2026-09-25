import QtQuick
import QtQuick.Controls

Item {
    id: cropOverlay
    anchors.fill: parent

    // Target image display rectangle within preview area
    property real imgX: 0
    property real imgY: 0
    property real imgW: width
    property real imgH: height

    readonly property real boxX: imgX + ((typeof cropController !== "undefined" && cropController) ? cropController.cropX * imgW : 0)
    readonly property real boxY: imgY + ((typeof cropController !== "undefined" && cropController) ? cropController.cropY * imgH : 0)
    readonly property real boxW: (typeof cropController !== "undefined" && cropController) ? cropController.cropWidth * imgW : imgW
    readonly property real boxH: (typeof cropController !== "undefined" && cropController) ? cropController.cropHeight * imgH : imgH

    // 1. Surrounding Dark Mask
    // Top Mask
    Rectangle {
        x: 0; y: 0; width: parent.width; height: Math.max(0, cropOverlay.boxY)
        color: "#000000"
        opacity: 0.55
    }
    // Bottom Mask
    Rectangle {
        x: 0
        y: cropOverlay.boxY + cropOverlay.boxH
        width: parent.width
        height: Math.max(0, parent.height - (cropOverlay.boxY + cropOverlay.boxH))
        color: "#000000"
        opacity: 0.55
    }
    // Left Mask
    Rectangle {
        x: 0
        y: cropOverlay.boxY
        width: Math.max(0, cropOverlay.boxX)
        height: cropOverlay.boxH
        color: "#000000"
        opacity: 0.55
    }
    // Right Mask
    Rectangle {
        x: cropOverlay.boxX + cropOverlay.boxW
        y: cropOverlay.boxY
        width: Math.max(0, parent.width - (cropOverlay.boxX + cropOverlay.boxW))
        height: cropOverlay.boxH
        color: "#000000"
        opacity: 0.55
    }

    // 2. Active Crop Window
    Rectangle {
        id: cropBox
        x: cropOverlay.boxX
        y: cropOverlay.boxY
        width: cropOverlay.boxW
        height: cropOverlay.boxH
        color: "transparent"
        border.color: "#818cf8"
        border.width: 2

        // Rule of Thirds Grid Lines
        // Horizontal Line 1
        Rectangle {
            x: 0; y: parent.height / 3; width: parent.width; height: 1
            color: "#ffffff"; opacity: 0.35
        }
        // Horizontal Line 2
        Rectangle {
            x: 0; y: (parent.height * 2) / 3; width: parent.width; height: 1
            color: "#ffffff"; opacity: 0.35
        }
        // Vertical Line 1
        Rectangle {
            x: parent.width / 3; y: 0; width: 1; height: parent.height
            color: "#ffffff"; opacity: 0.35
        }
        // Vertical Line 2
        Rectangle {
            x: (parent.width * 2) / 3; y: 0; width: 1; height: parent.height
            color: "#ffffff"; opacity: 0.35
        }

        // Draggable Area for moving box
        MouseArea {
            id: dragArea
            anchors.fill: parent
            cursorShape: Qt.SizeAllCursor
            drag.target: null

            property real startMouseX: 0
            property real startMouseY: 0
            property real startCropX: 0
            property real startCropY: 0

            onPressed: function(mouse) {
                startMouseX = mouse.x
                startMouseY = mouse.y
                if (typeof cropController !== "undefined" && cropController) {
                    startCropX = cropController.cropX
                    startCropY = cropController.cropY
                }
            }

            onPositionChanged: function(mouse) {
                if (!pressed || cropOverlay.imgW <= 0 || cropOverlay.imgH <= 0) return
                if (typeof cropController === "undefined" || !cropController) return

                var deltaX = (mouse.x - startMouseX) / cropOverlay.imgW
                var deltaY = (mouse.y - startMouseY) / cropOverlay.imgH

                var newX = Math.max(0.0, Math.min(1.0 - cropController.cropWidth, startCropX + deltaX))
                var newY = Math.max(0.0, Math.min(1.0 - cropController.cropHeight, startCropY + deltaY))

                cropController.setNormalizedCrop(newX, newY, cropController.cropWidth, cropController.cropHeight)
            }
        }

        // Corner Handles
        // Top-Left
        Rectangle {
            width: 10; height: 10; radius: 2; color: "#ffffff"; border.color: "#4f46e5"
            anchors.centerIn: parent.topLeft
        }
        // Top-Right
        Rectangle {
            width: 10; height: 10; radius: 2; color: "#ffffff"; border.color: "#4f46e5"
            anchors.centerIn: parent.topRight
        }
        // Bottom-Left
        Rectangle {
            width: 10; height: 10; radius: 2; color: "#ffffff"; border.color: "#4f46e5"
            anchors.centerIn: parent.bottomLeft
        }
        // Bottom-Right
        Rectangle {
            width: 10; height: 10; radius: 2; color: "#ffffff"; border.color: "#4f46e5"
            anchors.centerIn: parent.bottomRight
        }
    }
}
