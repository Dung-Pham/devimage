import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: previewRoot
    objectName: "previewCanvas"
    color: "#0d0f14"
    clip: true

    property string imageSource: ""
    property real zoomLevel: 1.0
    property real minZoom: 0.1
    property real maxZoom: 8.0

    property int originalWidth: previewImage.sourceSize.width
    property int originalHeight: previewImage.sourceSize.height

    function formatSourceUrl(src) {
        if (!src) return ""
        if (typeof backend !== "undefined" && backend && backend.pathToUrl) {
            return backend.pathToUrl(src)
        }
        if (src.indexOf("file:") === 0 || src.indexOf("qrc:") === 0 || src.indexOf("http:") === 0 || src.indexOf("https:") === 0) {
            return src
        }
        var clean = src.replace(/\\/g, "/")
        if (clean.charAt(0) === "/") {
            return "file://" + clean
        }
        return "file:///" + clean
    }

    function fitToView() {
        if (originalWidth > 0 && originalHeight > 0 && flickable.width > 0 && flickable.height > 0) {
            var scaleX = (flickable.width - 40) / originalWidth
            var scaleY = (flickable.height - 40) / originalHeight
            zoomLevel = Math.min(Math.min(scaleX, scaleY), 1.0)
            centerImage()
        }
    }

    function resetZoom() {
        zoomLevel = 1.0
        centerImage()
    }

    function centerImage() {
        flickable.contentX = Math.max(0, (contentContainer.width - flickable.width) / 2)
        flickable.contentY = Math.max(0, (contentContainer.height - flickable.height) / 2)
    }

    // Checkerboard transparency background pattern
    Canvas {
        id: checkerboard
        anchors.fill: parent
        onPaint: {
            var ctx = getContext("2d")
            var size = 16
            for (var x = 0; x < width; x += size) {
                for (var y = 0; y < height; y += size) {
                    ctx.fillStyle = ((x / size + y / size) % 2 === 0) ? "#141720" : "#0e1017"
                    ctx.fillRect(x, y, size, size)
                }
            }
        }
    }

    // Pan & Zoom Flickable Canvas
    Flickable {
        id: flickable
        anchors.fill: parent
        contentWidth: Math.max(contentContainer.width, width)
        contentHeight: Math.max(contentContainer.height, height)
        boundsBehavior: Flickable.StopAtBounds

        Item {
            id: contentContainer
            width: Math.max(previewImage.width + 60, flickable.width)
            height: Math.max(previewImage.height + 60, flickable.height)

            Image {
                id: previewImage
                anchors.centerIn: parent
                source: previewRoot.formatSourceUrl(previewRoot.imageSource)
                fillMode: Image.PreserveAspectFit
                smooth: true
                cache: false

                width: sourceSize.width > 0 ? sourceSize.width * previewRoot.zoomLevel : 0
                height: sourceSize.height > 0 ? sourceSize.height * previewRoot.zoomLevel : 0

                onStatusChanged: {
                    if (status === Image.Ready) {
                        previewRoot.fitToView()
                    } else if (status === Image.Error) {
                        console.error("ImagePreview: Failed to load image from source:", source)
                    }
                }

                onSourceSizeChanged: {
                    if (status === Image.Ready) {
                        previewRoot.fitToView()
                    }
                }
            }
        }

        // Wheel Zoom Support
        WheelHandler {
            target: flickable
            onWheel: function(event) {
                if (event.angleDelta.y > 0) {
                    previewRoot.zoomLevel = Math.min(previewRoot.maxZoom, previewRoot.zoomLevel * 1.15)
                } else if (event.angleDelta.y < 0) {
                    previewRoot.zoomLevel = Math.max(previewRoot.minZoom, previewRoot.zoomLevel / 1.15)
                }
            }
        }
    }

    // Floating Zoom Controls (Bottom Right)
    Rectangle {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 18
        height: 38
        radius: 8
        color: "#181b24"
        border.color: "#2e3549"
        implicitWidth: zoomRow.implicitWidth + 16

        RowLayout {
            id: zoomRow
            anchors.centerIn: parent
            spacing: 8

            Button {
                text: "−"
                font.bold: true
                font.pixelSize: 15
                contentItem: Text { text: "−"; font.bold: true; color: "#f8fafc"; horizontalAlignment: Text.AlignHCenter }
                background: Rectangle { implicitWidth: 26; implicitHeight: 26; radius: 4; color: "#222634" }
                onClicked: previewRoot.zoomLevel = Math.max(previewRoot.minZoom, previewRoot.zoomLevel / 1.2)
            }

            Text {
                text: Math.round(previewRoot.zoomLevel * 100) + "%"
                font.pixelSize: 12
                font.bold: true
                color: "#38bdf8"
                Layout.preferredWidth: 44
                horizontalAlignment: Text.AlignHCenter
            }

            Button {
                text: "+"
                font.bold: true
                font.pixelSize: 15
                contentItem: Text { text: "+"; font.bold: true; color: "#f8fafc"; horizontalAlignment: Text.AlignHCenter }
                background: Rectangle { implicitWidth: 26; implicitHeight: 26; radius: 4; color: "#222634" }
                onClicked: previewRoot.zoomLevel = Math.min(previewRoot.maxZoom, previewRoot.zoomLevel * 1.2)
            }

            Rectangle { width: 1; height: 18; color: "#2e3549" }

            Button {
                text: "Fit"
                font.pixelSize: 11
                contentItem: Text { text: "Fit"; color: "#cbd5e1"; horizontalAlignment: Text.AlignHCenter }
                background: Rectangle { implicitWidth: 32; implicitHeight: 26; radius: 4; color: "#222634" }
                onClicked: previewRoot.fitToView()
            }

            Button {
                text: "1:1"
                font.pixelSize: 11
                contentItem: Text { text: "1:1"; color: "#cbd5e1"; horizontalAlignment: Text.AlignHCenter }
                background: Rectangle { implicitWidth: 32; implicitHeight: 26; radius: 4; color: "#222634" }
                onClicked: previewRoot.resetZoom()
            }
        }
    }

    // Resolution & Format Badge (Bottom Left)
    Rectangle {
        visible: previewRoot.originalWidth > 0
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 18
        height: 32
        radius: 6
        color: "#181b24"
        border.color: "#2e3549"
        implicitWidth: resText.implicitWidth + 20

        Text {
            id: resText
            anchors.centerIn: parent
            text: previewRoot.originalWidth + " × " + previewRoot.originalHeight + " px"
            font.pixelSize: 12
            font.bold: true
            color: "#94a3b8"
        }
    }
}
