import QtQuick
import QtQuick.Controls

Item {
    id: pickerOverlay

    property real imgX: 0
    property real imgY: 0
    property real imgW: 0
    property real imgH: 0
    property real origW: 0
    property real origH: 0

    visible: false

    MouseArea {
        id: pickArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.CrossCursor

        function updateSample(mouseX, mouseY) {
            if (imgW <= 0 || imgH <= 0 || origW <= 0 || origH <= 0) return
            var relX = (mouseX - imgX) / imgW
            var relY = (mouseY - imgY) / imgH

            if (relX >= 0 && relX <= 1 && relY >= 0 && relY <= 1) {
                var px = Math.min(origW - 1, Math.max(0, Math.floor(relX * origW)))
                var py = Math.min(origH - 1, Math.max(0, Math.floor(relY * origH)))
                if (typeof colorPickerController !== "undefined" && colorPickerController) {
                    colorPickerController.sampleAt(px, py)
                }
            }
        }

        onPositionChanged: function(mouse) {
            updateSample(mouse.x, mouse.y)
        }

        onClicked: function(mouse) {
            updateSample(mouse.x, mouse.y)
            pulseAnimation.restart()
        }
    }

    // Floating loupe / color indicator next to cursor
    Rectangle {
        id: cursorIndicator
        visible: pickArea.containsMouse && (pickArea.mouseX >= imgX && pickArea.mouseX <= imgX + imgW && pickArea.mouseY >= imgY && pickArea.mouseY <= imgY + imgH)
        x: pickArea.mouseX + 16
        y: pickArea.mouseY - 32
        width: 32
        height: 32
        radius: 16
        color: (typeof colorPickerController !== "undefined" && colorPickerController) ? colorPickerController.currentHex : "#ffffff"
        border.color: "#ffffff"
        border.width: 2

        // Pulse scale animation on click
        scale: 1.0
        SequentialAnimation {
            id: pulseAnimation
            NumberAnimation { target: cursorIndicator; property: "scale"; to: 1.4; duration: 100; easing.type: Easing.OutQuad }
            NumberAnimation { target: cursorIndicator; property: "scale"; to: 1.0; duration: 120; easing.type: Easing.InQuad }
        }
    }
}
