import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: inspectorView
    clip: true
    ScrollBar.vertical.policy: ScrollBar.AsNeeded

    ColumnLayout {
        width: parent.width
        spacing: 14

        // Placeholder when no image is loaded
        Rectangle {
            Layout.fillWidth: true
            height: 90
            radius: 8
            color: "#1a1e2a"
            border.color: "#262b3a"
            visible: !inspectorController || !inspectorController.hasData

            Text {
                anchors.centerIn: parent
                text: "Select or drop an image\nto view technical metadata."
                font.pixelSize: 12
                color: "#64748b"
                horizontalAlignment: Text.AlignHCenter
            }
        }

        // Active Metadata Cards
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 12
            visible: inspectorController && inspectorController.hasData

            // 1. Quick Copy Action Row
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Button {
                    Layout.fillWidth: true
                    height: 32
                    text: "📋 Copy Report"
                    font.pixelSize: 11
                    font.bold: true
                    contentItem: Text {
                        text: parent.text
                        color: "#f8fafc"
                        font.pixelSize: 11
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        radius: 6
                        color: parent.hovered ? "#4f46e5" : "#4338ca"
                    }
                    onClicked: inspectorController.copyAll()
                }

                Button {
                    Layout.fillWidth: true
                    height: 32
                    text: "{ } Copy JSON"
                    font.pixelSize: 11
                    font.bold: true
                    contentItem: Text {
                        text: parent.text
                        color: "#38bdf8"
                        font.pixelSize: 11
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        radius: 6
                        color: parent.hovered ? "#1e293b" : "#0f172a"
                        border.color: "#38bdf8"
                    }
                    onClicked: inspectorController.copyJson()
                }
            }

            // 2. Geometry Card
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: geoCol.implicitHeight + 20
                radius: 8
                color: "#1a1e2a"
                border.color: "#262b3a"

                ColumnLayout {
                    id: geoCol
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 6

                    Text {
                        text: "GEOMETRY"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#818cf8"
                        font.letterSpacing: 1.0
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Dimensions:"; color: "#94a3b8"; font.pixelSize: 11; Layout.fillWidth: true }
                        Text { text: inspectorController ? inspectorController.dimensions + " px" : ""; color: "#f8fafc"; font.pixelSize: 11; font.bold: true }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Aspect Ratio:"; color: "#94a3b8"; font.pixelSize: 11; Layout.fillWidth: true }
                        Text { text: inspectorController ? inspectorController.aspectRatio : ""; color: "#f8fafc"; font.pixelSize: 11 }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Density (DPI):"; color: "#94a3b8"; font.pixelSize: 11; Layout.fillWidth: true }
                        Text { text: inspectorController ? inspectorController.dpi : ""; color: "#cbd5e1"; font.pixelSize: 11 }
                    }
                }
            }

            // 3. File Info Card
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: fileCol.implicitHeight + 20
                radius: 8
                color: "#1a1e2a"
                border.color: "#262b3a"

                ColumnLayout {
                    id: fileCol
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 6

                    Text {
                        text: "FILE DETAILS"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#38bdf8"
                        font.letterSpacing: 1.0
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Format:"; color: "#94a3b8"; font.pixelSize: 11; Layout.fillWidth: true }
                        Text { text: inspectorController ? inspectorController.format : ""; color: "#f8fafc"; font.pixelSize: 11; font.bold: true }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "File Size:"; color: "#94a3b8"; font.pixelSize: 11; Layout.fillWidth: true }
                        Text { text: inspectorController ? inspectorController.fileSize : ""; color: "#f8fafc"; font.pixelSize: 11; font.bold: true }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Filename:"; color: "#94a3b8"; font.pixelSize: 11; Layout.fillWidth: true }
                        Text {
                            text: inspectorController ? inspectorController.fileName : ""
                            color: "#cbd5e1"
                            font.pixelSize: 11
                            elide: Text.ElideMiddle
                            Layout.maximumWidth: 160
                        }
                    }
                }
            }

            // 4. Color & Channels Card
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: colorCol.implicitHeight + 20
                radius: 8
                color: "#1a1e2a"
                border.color: "#262b3a"

                ColumnLayout {
                    id: colorCol
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 6

                    Text {
                        text: "COLOR & CHANNELS"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#a78bfa"
                        font.letterSpacing: 1.0
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Color Mode:"; color: "#94a3b8"; font.pixelSize: 11; Layout.fillWidth: true }
                        Text { text: inspectorController ? inspectorController.colorMode : ""; color: "#f8fafc"; font.pixelSize: 11 }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Transparency (Alpha):"; color: "#94a3b8"; font.pixelSize: 11; Layout.fillWidth: true }
                        Text {
                            text: inspectorController && inspectorController.hasAlpha ? "Present (4-channel)" : "None (Opaque)"
                            color: inspectorController && inspectorController.hasAlpha ? "#4ade80" : "#94a3b8"
                            font.pixelSize: 11
                            font.bold: inspectorController ? inspectorController.hasAlpha : false
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Color Profile:"; color: "#94a3b8"; font.pixelSize: 11; Layout.fillWidth: true }
                        Text { text: inspectorController ? inspectorController.colorSpace : ""; color: "#cbd5e1"; font.pixelSize: 10; elide: Text.ElideRight; Layout.maximumWidth: 150 }
                    }
                }
            }

            // 5. Optimization Advice Card
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: optCol.implicitHeight + 20
                radius: 8
                color: "#1a1e2a"
                border.color: "#262b3a"

                ColumnLayout {
                    id: optCol
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 6

                    Text {
                        text: "OPTIMIZATION ADVICE"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#f59e0b"
                        font.letterSpacing: 1.0
                    }

                    Repeater {
                        model: inspectorController ? inspectorController.optimizationTips : []
                        Text {
                            text: "• " + modelData
                            color: "#cbd5e1"
                            font.pixelSize: 11
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                }
            }

            // 6. EXIF Metadata (if available)
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: exifCol.implicitHeight + 20
                radius: 8
                color: "#1a1e2a"
                border.color: "#262b3a"
                visible: inspectorController && inspectorController.hasExif

                ColumnLayout {
                    id: exifCol
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 6

                    Text {
                        text: "EXIF DATA (" + (inspectorController ? inspectorController.exifCount : 0) + " tags)"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#34d399"
                        font.letterSpacing: 1.0
                    }

                    Repeater {
                        model: inspectorController ? inspectorController.exifList : []
                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: modelData.key + ":"
                                color: "#94a3b8"
                                font.pixelSize: 10
                                Layout.preferredWidth: 90
                                elide: Text.ElideRight
                            }
                            Text {
                                text: modelData.value
                                color: "#f8fafc"
                                font.pixelSize: 10
                                elide: Text.ElideMiddle
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
            }
        }
    }
}
