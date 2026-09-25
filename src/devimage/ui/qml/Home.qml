import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

ScrollView {
    id: homeScroll
    clip: true
    ScrollBar.vertical.policy: ScrollBar.AsNeeded

    signal toolSelected(string toolId, string toolTitle)

    property string filterQuery: searchBar.text.toLowerCase().trim()

    function matchesFilter(title, desc) {
        if (!filterQuery) return true
        return title.toLowerCase().indexOf(filterQuery) !== -1 ||
               desc.toLowerCase().indexOf(filterQuery) !== -1
    }

    ColumnLayout {
        width: Math.min(homeScroll.width - 48, 1020)
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 28
        anchors.topMargin: 24
        anchors.bottomMargin: 32

        // Hero Search & Header
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 12

            Text {
                text: "Select a Tool"
                font.pixelSize: 22
                font.bold: true
                color: "#f8fafc"
            }

            Text {
                text: "Fast, offline-first image manipulation toolkit tailored for developers and technical creators."
                font.pixelSize: 13
                color: "#94a3b8"
            }

            SearchInput {
                id: searchBar
                Layout.fillWidth: true
                Layout.topMargin: 4
            }
        }

        // Section 1: IMAGE TOOLS
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 12

            Text {
                text: "IMAGE TOOLS"
                font.pixelSize: 12
                font.bold: true
                color: "#818cf8"
                font.letterSpacing: 1.2
            }

            Flow {
                Layout.fillWidth: true
                spacing: 14

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "remove_background"
                    title: "Remove Background"
                    description: "Erase backgrounds with offline AI"
                    iconGlyph: "✨"
                    onClicked: homeScroll.toolSelected(toolId, title)
                }

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "resize"
                    title: "Resize"
                    description: "Smart dimensions & aspect ratio scaling"
                    iconGlyph: "📐"
                    onClicked: homeScroll.toolSelected(toolId, title)
                }

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "compress"
                    title: "Compress"
                    description: "Reduce file sizes with quality control"
                    iconGlyph: "🗜"
                    onClicked: homeScroll.toolSelected(toolId, title)
                }

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "convert"
                    title: "Convert"
                    description: "Batch transcode PNG, JPG, WebP, AVIF"
                    iconGlyph: "🔄"
                    onClicked: homeScroll.toolSelected(toolId, title)
                }

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "crop"
                    title: "Crop"
                    description: "Custom boxes, ratios, and circle crop"
                    iconGlyph: "✂"
                    onClicked: homeScroll.toolSelected(toolId, title)
                }
            }
        }

        // Section 2: DEVELOPER TOOLS
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 12

            Text {
                text: "DEVELOPER TOOLS"
                font.pixelSize: 12
                font.bold: true
                color: "#38bdf8"
                font.letterSpacing: 1.2
            }

            Flow {
                Layout.fillWidth: true
                spacing: 14

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "inspector"
                    title: "Image Inspector"
                    description: "Inspect EXIF metadata, DPI, and channels"
                    iconGlyph: "🔍"
                    onClicked: homeScroll.toolSelected(toolId, title)
                }

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "color_picker"
                    title: "Color Picker"
                    description: "Sample pixels, hex, and RGBA codes"
                    iconGlyph: "🎨"
                    onClicked: homeScroll.toolSelected(toolId, title)
                }

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "ocr"
                    title: "OCR"
                    description: "Extract text locally from images"
                    iconGlyph: "📝"
                    onClicked: homeScroll.toolSelected(toolId, title)
                }

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "rename"
                    title: "Rename"
                    description: "Template-based batch file renaming"
                    iconGlyph: "🏷"
                    onClicked: homeScroll.toolSelected(toolId, title)
                }

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "copy_path"
                    title: "Copy Path"
                    description: "Quick copy URI, POSIX, or relative path"
                    iconGlyph: "📋"
                    onClicked: homeScroll.toolSelected(toolId, title)
                }
            }
        }

        // Section 3: AI TOOLS
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 12

            Text {
                text: "AI TOOLS"
                font.pixelSize: 12
                font.bold: true
                color: "#c084fc"
                font.letterSpacing: 1.2
            }

            Flow {
                Layout.fillWidth: true
                spacing: 14

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "analyze"
                    title: "Analyze Image"
                    description: "Semantic scene and content analysis"
                    iconGlyph: "🧠"
                    isAi: true
                    onClicked: homeScroll.toolSelected(toolId, title)
                }

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "alt_text"
                    title: "Generate Alt Text"
                    description: "Accessibility description for web images"
                    iconGlyph: "💬"
                    isAi: true
                    onClicked: homeScroll.toolSelected(toolId, title)
                }

                ToolCard {
                    visible: homeScroll.matchesFilter(title, description)
                    toolId: "ai_command"
                    title: "AI Command"
                    description: "Natural language image editing prompt"
                    iconGlyph: "⚡"
                    isAi: true
                    onClicked: homeScroll.toolSelected(toolId, title)
                }
            }
        }
    }
}
