import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: renameTool
    Layout.fillWidth: true
    Layout.fillHeight: true
    clip: true
    contentWidth: availableWidth
    ScrollBar.vertical.policy: ScrollBar.AsNeeded

    readonly property var ctrl: (typeof renameController !== "undefined" && renameController) ? renameController : ((typeof backend !== "undefined" && backend && backend.renameController) ? backend.renameController : null)

    ColumnLayout {
        width: renameTool.availableWidth
        spacing: 14

        // 1. Status & Summary Card
        Rectangle {
            Layout.fillWidth: true
            height: 64
            radius: 8
            color: "#1a1e2a"
            border.color: (ctrl && ctrl.hasCollisions) ? "#ef4444" : "#262b3a"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                Rectangle {
                    width: 38
                    height: 38
                    radius: 6
                    color: (ctrl && ctrl.hasCollisions) ? "#7f1d1d" : ((ctrl && ctrl.hasFiles) ? "#14532d" : "#262b3a")

                    Text {
                        anchors.centerIn: parent
                        text: (ctrl && ctrl.hasCollisions) ? "⚠️" : ((ctrl && ctrl.hasFiles) ? "📋" : "📁")
                        font.pixelSize: 18
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    RowLayout {
                        spacing: 8
                        Text {
                            text: "BATCH QUEUE"
                            font.pixelSize: 10
                            font.bold: true
                            color: "#64748b"
                        }
                        Text {
                            text: (ctrl ? ctrl.fileCount : 0) + " files"
                            font.pixelSize: 11
                            font.bold: true
                            color: "#38bdf8"
                        }
                    }

                    Text {
                        text: ctrl ? ctrl.statusMessage : "No files queued"
                        font.pixelSize: 12
                        font.bold: true
                        color: (ctrl && ctrl.hasCollisions) ? "#f87171" : ((ctrl && ctrl.hasFiles) ? "#34d399" : "#94a3b8")
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }
            }
        }

        // 2. Presets Selection
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            Text {
                text: "PRESETS"
                font.pixelSize: 10
                font.bold: true
                color: "#64748b"
            }

            Flow {
                Layout.fillWidth: true
                spacing: 6

                Repeater {
                    model: [
                        { label: "Numbered", id: "numbered" },
                        { label: "Date & Name", id: "date_name" },
                        { label: "Dimensions", id: "dimensions" },
                        { label: "kebab-case", id: "kebab" },
                        { label: "snake_case", id: "snake" },
                        { label: "img_{n}", id: "clean_number" }
                    ]

                    Rectangle {
                        height: 28
                        implicitWidth: presetText.implicitWidth + 16
                        radius: 6
                        color: presetMouse.containsMouse ? "#2a3042" : "#1a1e2a"
                        border.color: "#333b4f"

                        Text {
                            id: presetText
                            anchors.centerIn: parent
                            text: modelData.label
                            font.pixelSize: 11
                            color: "#cbd5e1"
                        }

                        MouseArea {
                            id: presetMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (ctrl) ctrl.applyPreset(modelData.id)
                            }
                        }
                    }
                }
            }
        }

        // 3. Pattern Input & Tokens
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            Text {
                text: "NAMING PATTERN"
                font.pixelSize: 10
                font.bold: true
                color: "#64748b"
            }

            Rectangle {
                Layout.fillWidth: true
                height: 38
                radius: 6
                color: "#0f1117"
                border.color: patternField.activeFocus ? "#6366f1" : "#262b3a"

                TextInput {
                    id: patternField
                    anchors.fill: parent
                    anchors.leftMargin: 10
                    anchors.rightMargin: 10
                    verticalAlignment: Text.AlignVCenter
                    color: "#f8fafc"
                    font.pixelSize: 13
                    font.bold: true
                    text: ctrl ? ctrl.pattern : "{name}_{n}"
                    selectByMouse: true

                    onTextEdited: {
                        if (ctrl) ctrl.setPattern(text)
                    }
                }
            }

            // Quick token insert chips
            Flow {
                Layout.fillWidth: true
                spacing: 4

                Repeater {
                    model: ["{name}", "{n}", "{date}", "{w}", "{h}", "{ext}"]

                    Rectangle {
                        height: 22
                        implicitWidth: tokenLabel.implicitWidth + 10
                        radius: 4
                        color: tokenMouse.containsMouse ? "#3730a3" : "#1e1b4b"
                        border.color: "#4338ca"

                        Text {
                            id: tokenLabel
                            anchors.centerIn: parent
                            text: modelData
                            font.pixelSize: 10
                            font.family: "monospace"
                            color: "#a5b4fc"
                        }

                        MouseArea {
                            id: tokenMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                var cur = patternField.text
                                var pos = patternField.cursorPosition
                                var nextText = cur.slice(0, pos) + modelData + cur.slice(pos)
                                patternField.text = nextText
                                if (ctrl) ctrl.setPattern(nextText)
                                patternField.cursorPosition = pos + modelData.length
                            }
                        }
                    }
                }
            }
        }

        // 4. Numbering & Indexing
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4

                Text {
                    text: "START INDEX"
                    font.pixelSize: 10
                    font.bold: true
                    color: "#64748b"
                }

                SpinBox {
                    id: startIndexSpin
                    Layout.fillWidth: true
                    from: 0
                    to: 9999
                    value: ctrl ? ctrl.startIndex : 1
                    editable: true
                    onValueModified: {
                        if (ctrl) ctrl.setStartIndex(value)
                    }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4

                Text {
                    text: "ZERO PADDING"
                    font.pixelSize: 10
                    font.bold: true
                    color: "#64748b"
                }

                SpinBox {
                    id: paddingSpin
                    Layout.fillWidth: true
                    from: 1
                    to: 8
                    value: ctrl ? ctrl.padding : 3
                    editable: true
                    onValueModified: {
                        if (ctrl) ctrl.setPadding(value)
                    }
                }
            }
        }

        // 5. Case Transformation
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            Text {
                text: "CASE CONVERSION"
                font.pixelSize: 10
                font.bold: true
                color: "#64748b"
            }

            ComboBox {
                id: caseCombo
                Layout.fillWidth: true
                model: [
                    { text: "Original Case", val: "none" },
                    { text: "lowercase", val: "lowercase" },
                    { text: "UPPERCASE", val: "uppercase" },
                    { text: "kebab-case", val: "kebab-case" },
                    { text: "snake_case", val: "snake_case" },
                    { text: "Title Case", val: "title" }
                ]
                textRole: "text"
                currentIndex: 0
                onActivated: function(index) {
                    var item = model[index]
                    if (ctrl && item) {
                        ctrl.setCaseTransform(item.val)
                    }
                }
            }
        }

        // 6. Find & Replace
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            Text {
                text: "FIND & REPLACE"
                font.pixelSize: 10
                font.bold: true
                color: "#64748b"
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                Rectangle {
                    Layout.fillWidth: true
                    height: 32
                    radius: 6
                    color: "#0f1117"
                    border.color: "#262b3a"

                    TextField {
                        id: findInput
                        anchors.fill: parent
                        anchors.margins: 4
                        verticalAlignment: Text.AlignVCenter
                        color: "#f8fafc"
                        font.pixelSize: 12
                        placeholderText: "Find..."
                        placeholderTextColor: "#64748b"
                        background: Item {}
                        onTextEdited: {
                            if (ctrl) ctrl.setFindReplace(text, replaceInput.text)
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 32
                    radius: 6
                    color: "#0f1117"
                    border.color: "#262b3a"

                    TextField {
                        id: replaceInput
                        anchors.fill: parent
                        anchors.margins: 4
                        verticalAlignment: Text.AlignVCenter
                        color: "#f8fafc"
                        font.pixelSize: 12
                        placeholderText: "Replace..."
                        placeholderTextColor: "#64748b"
                        background: Item {}
                        onTextEdited: {
                            if (ctrl) ctrl.setFindReplace(findInput.text, text)
                        }
                    }
                }
            }
        }

        // 7. Workspace Actions (Add current image / Clear)
        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Button {
                id: addCurrentBtn
                Layout.fillWidth: true
                height: 32
                text: "+ Add Active Image"
                font.pixelSize: 11
                font.bold: true
                enabled: toolShell.currentImagePath && toolShell.currentImagePath.length > 0
                contentItem: Text {
                    text: addCurrentBtn.text
                    color: addCurrentBtn.enabled ? "#38bdf8" : "#475569"
                    font.pixelSize: 11
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    radius: 6
                    color: addCurrentBtn.hovered ? "#1e293b" : "#0f172a"
                    border.color: addCurrentBtn.enabled ? "#38bdf8" : "#334155"
                }
                onClicked: {
                    if (ctrl && toolShell.currentImagePath) {
                        ctrl.addFile(toolShell.currentImagePath)
                    }
                }
            }

            Button {
                id: clearAllBtn
                height: 32
                implicitWidth: 80
                text: "Clear All"
                font.pixelSize: 11
                enabled: ctrl && ctrl.hasFiles
                contentItem: Text {
                    text: clearAllBtn.text
                    color: clearAllBtn.enabled ? "#f87171" : "#475569"
                    font.pixelSize: 11
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    radius: 6
                    color: clearAllBtn.hovered ? "#450a0a" : "#1c1917"
                    border.color: clearAllBtn.enabled ? "#7f1d1d" : "#292524"
                }
                onClicked: {
                    if (ctrl) ctrl.clearFiles()
                }
            }
        }

        // 8. Compact Preview List in Sidebar
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6
            visible: ctrl && ctrl.hasFiles

            RowLayout {
                Layout.fillWidth: true
                Text {
                    text: "QUEUE PREVIEW"
                    font.pixelSize: 10
                    font.bold: true
                    color: "#64748b"
                }
                Item { Layout.fillWidth: true }
                Text {
                    text: (ctrl ? ctrl.readyCount : 0) + " ready"
                    font.pixelSize: 10
                    color: "#34d399"
                }
            }

            Repeater {
                model: ctrl ? ctrl.previews : []

                Rectangle {
                    Layout.fillWidth: true
                    height: 48
                    radius: 6
                    color: modelData.status === "collision" ? "#450a0a" : (modelData.status === "exists" ? "#451a03" : "#1a1e2a")
                    border.color: modelData.status === "collision" ? "#ef4444" : (modelData.status === "exists" ? "#f59e0b" : "#262b3a")

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 8

                        Text {
                            text: modelData.status === "ok" ? "✓" : (modelData.status === "collision" ? "✕" : "!")
                            font.pixelSize: 12
                            font.bold: true
                            color: modelData.status === "ok" ? "#34d399" : (modelData.status === "collision" ? "#f87171" : "#fbbf24")
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 1

                            Text {
                                text: modelData.source_name
                                font.pixelSize: 11
                                color: "#94a3b8"
                                elide: Text.ElideMiddle
                                Layout.fillWidth: true
                            }

                            Text {
                                text: "→ " + modelData.target_name
                                font.pixelSize: 11
                                font.bold: true
                                color: modelData.status === "collision" ? "#fca5a5" : "#38bdf8"
                                elide: Text.ElideMiddle
                                Layout.fillWidth: true
                            }
                        }

                        // Remove button
                        Button {
                            implicitWidth: 24
                            implicitHeight: 24
                            contentItem: Text {
                                text: "×"
                                color: "#94a3b8"
                                font.pixelSize: 14
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            background: Rectangle {
                                radius: 4
                                color: parent.hovered ? "#334155" : "transparent"
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
