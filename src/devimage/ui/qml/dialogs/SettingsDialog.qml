import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: settingsDlg
    anchors.centerIn: parent
    width: Math.min(parent ? parent.width - 48 : 520, 540)
    modal: true
    title: ""
    padding: 0

    background: Rectangle {
        color: "#161922"
        radius: 12
        border.color: "#2e3549"
        border.width: 1
    }

    contentItem: ColumnLayout {
        spacing: 0

        // Header
        Rectangle {
            Layout.fillWidth: true
            height: 52
            color: "#1c202c"
            radius: 12

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 20
                anchors.rightMargin: 16

                Text {
                    text: "⚙ Application Preferences"
                    font.pixelSize: 16
                    font.bold: true
                    color: "#f8fafc"
                    Layout.fillWidth: true
                }

                Button {
                    text: "✕"
                    font.pixelSize: 12
                    contentItem: Text { text: "✕"; color: "#94a3b8"; horizontalAlignment: Text.AlignHCenter }
                    background: Rectangle { implicitWidth: 24; implicitHeight: 24; radius: 12; color: "transparent" }
                    onClicked: settingsDlg.close()
                }
            }
        }

        // Settings Body
        ColumnLayout {
            Layout.fillWidth: true
            Layout.margins: 22
            spacing: 20

            // 1. Theme Mode
            ColumnLayout {
                spacing: 6
                Text {
                    text: "Visual Theme"
                    font.bold: true
                    font.pixelSize: 13
                    color: "#f1f5f9"
                }

                RowLayout {
                    spacing: 20
                    RadioButton {
                        id: darkRadio
                        text: "Dark"
                        checked: backend ? backend.settings.get("theme", "dark") === "dark" : true
                        onClicked: {
                            if (backend) backend.settings.set("theme", "dark")
                        }
                    }
                    RadioButton {
                        id: lightRadio
                        text: "Light"
                        checked: backend ? backend.settings.get("theme", "dark") === "light" : false
                        onClicked: {
                            if (backend) backend.settings.set("theme", "light")
                        }
                    }
                    RadioButton {
                        id: systemRadio
                        text: "System"
                        checked: backend ? backend.settings.get("theme", "dark") === "system" : false
                        onClicked: {
                            if (backend) backend.settings.set("theme", "system")
                        }
                    }
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: "#262b3a" }

            // 2. Conflict Overwrite Mode
            RowLayout {
                Layout.fillWidth: true
                spacing: 16

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    Text { text: "File Overwrite Conflict"; font.bold: true; font.pixelSize: 13; color: "#f1f5f9" }
                    Text { text: "Action taken when output file already exists"; font.pixelSize: 12; color: "#94a3b8" }
                }

                ComboBox {
                    id: overwriteCombo
                    model: ["rename", "overwrite", "ask"]
                    currentIndex: {
                        var mode = backend ? backend.settings.get("overwrite_mode", "rename") : "rename"
                        return Math.max(0, model.indexOf(mode))
                    }
                    onActivated: {
                        if (backend) backend.settings.set("overwrite_mode", currentText)
                    }
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: "#262b3a" }

            // 3. Default Compression Quality
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                RowLayout {
                    Layout.fillWidth: true
                    Text { text: "Default Image Quality"; font.bold: true; font.pixelSize: 13; color: "#f1f5f9" }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: Math.round(qualitySlider.value) + "%"
                        font.bold: true
                        font.pixelSize: 13
                        color: "#38bdf8"
                    }
                }

                Slider {
                    id: qualitySlider
                    Layout.fillWidth: true
                    from: 10
                    to: 100
                    stepSize: 1
                    value: backend ? backend.settings.get("default_quality", 85) : 85
                    onMoved: {
                        if (backend) backend.settings.set("default_quality", Math.round(value))
                    }
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: "#262b3a" }

            // 4. Auto Preview Switch
            RowLayout {
                Layout.fillWidth: true
                spacing: 16

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    Text { text: "Auto-Generate Previews"; font.bold: true; font.pixelSize: 13; color: "#f1f5f9" }
                    Text { text: "Automatically render full preview upon loading an image"; font.pixelSize: 12; color: "#94a3b8" }
                }

                Switch {
                    id: previewSwitch
                    checked: backend ? backend.settings.get("auto_preview", true) : true
                    onToggled: {
                        if (backend) backend.settings.set("auto_preview", checked)
                    }
                }
            }

            // Dialog Actions
            RowLayout {
                Layout.fillWidth: true
                Layout.topMargin: 12

                Button {
                    text: "Reset to Defaults"
                    font.pixelSize: 12
                    contentItem: Text { text: "Reset to Defaults"; color: "#94a3b8" }
                    background: Rectangle { implicitWidth: 120; implicitHeight: 34; radius: 6; color: "transparent"; border.color: "#334155" }
                    onClicked: {
                        if (backend) {
                            backend.settings.resetToDefaults()
                            qualitySlider.value = backend.settings.get("default_quality", 85)
                            previewSwitch.checked = backend.settings.get("auto_preview", true)
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                Button {
                    text: "Done"
                    font.bold: true
                    font.pixelSize: 13
                    contentItem: Text { text: "Done"; font.bold: true; color: "#ffffff"; horizontalAlignment: Text.AlignHCenter }
                    background: Rectangle { implicitWidth: 80; implicitHeight: 34; radius: 6; color: "#6366f1" }
                    onClicked: settingsDlg.close()
                }
            }
        }
    }
}
