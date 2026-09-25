import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts

Rectangle {
    id: dropZone
    implicitWidth: 500
    implicitHeight: 280
    radius: 12
    color: dropArea.containsDrag ? "#1e1b4b" : (browseArea.containsMouse ? "#1a1d27" : "#13161f")
    border.color: dropArea.containsDrag ? "#818cf8" : (browseArea.containsMouse ? "#4f46e5" : "#2a3042")
    border.width: dropArea.containsDrag ? 2 : 1.5

    signal fileDropped(string filePath)

    Behavior on color { ColorAnimation { duration: 160 } }
    Behavior on border.color { ColorAnimation { duration: 160 } }

    DropArea {
        id: dropArea
        anchors.fill: parent

        onDropped: function(drop) {
            if (drop.hasUrls && drop.urls.length > 0) {
                var rawUrl = drop.urls[0].toString()
                if (backend) {
                    backend.openImageFile(rawUrl)
                }
                dropZone.fileDropped(rawUrl)
                drop.acceptProposedAction()
            }
        }
    }

    MouseArea {
        id: browseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: fileDialog.open()
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 14
        width: Math.min(parent.width - 40, 420)

        // Center Icon
        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            width: 60
            height: 60
            radius: 30
            color: dropArea.containsDrag ? "#312e81" : "#1c202e"
            border.color: dropArea.containsDrag ? "#6366f1" : "#2e3549"

            Text {
                anchors.centerIn: parent
                text: dropArea.containsDrag ? "📥" : "📁"
                font.pixelSize: 28
            }
        }

        // Headlines
        Text {
            text: dropArea.containsDrag ? "Drop image to load into workspace" : "Drag & drop an image here"
            font.pixelSize: 17
            font.bold: true
            color: dropArea.containsDrag ? "#c7d2fe" : "#f8fafc"
            Layout.alignment: Qt.AlignHCenter
        }

        Text {
            text: "or click anywhere to browse from your computer"
            font.pixelSize: 13
            color: "#94a3b8"
            Layout.alignment: Qt.AlignHCenter
        }

        // Action Button
        Button {
            id: browseBtn
            text: "Browse Image..."
            font.bold: true
            font.pixelSize: 13
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 4

            contentItem: Text {
                text: browseBtn.text
                font: browseBtn.font
                color: "#ffffff"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            background: Rectangle {
                implicitWidth: 140
                implicitHeight: 38
                radius: 8
                color: browseBtn.down ? "#4338ca" : (browseBtn.hovered ? "#4f46e5" : "#6366f1")
            }

            onClicked: fileDialog.open()
        }

        Text {
            text: "PNG • JPEG • WebP • AVIF • TIFF • BMP • GIF • ICO"
            font.pixelSize: 11
            color: "#64748b"
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 6
        }
    }

    // Native Qt FileDialog
    FileDialog {
        id: fileDialog
        title: "Select an Image"
        nameFilters: [
            "Image files (*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif *.gif *.ico *.avif)",
            "All files (*)"
        ]
        onAccepted: {
            if (fileDialog.selectedFile) {
                var rawUrl = fileDialog.selectedFile.toString()
                if (backend) {
                    backend.openImageFile(rawUrl)
                }
                dropZone.fileDropped(rawUrl)
            }
        }
    }
}
