import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: toastRoot
    anchors.horizontalCenter: parent ? parent.horizontalCenter : undefined
    anchors.bottom: parent ? parent.bottom : undefined
    anchors.bottomMargin: 48
    height: 48
    radius: 8
    visible: opacity > 0
    opacity: 0.0
    implicitWidth: toastContent.implicitWidth + 36

    property string toastType: "info"

    // Dynamic color palette based on severity
    color: {
        if (toastType === "error") return "#7f1d1d"
        if (toastType === "success") return "#064e3b"
        if (toastType === "warning") return "#78350f"
        return "#1e293b"
    }

    border.color: {
        if (toastType === "error") return "#ef4444"
        if (toastType === "success") return "#10b981"
        if (toastType === "warning") return "#f59e0b"
        return "#475569"
    }
    border.width: 1

    Behavior on opacity {
        NumberAnimation { duration: 220; easing.type: Easing.OutQuad }
    }

    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: toastRoot.opacity = 0.0
    }

    RowLayout {
        id: toastContent
        anchors.centerIn: parent
        spacing: 10

        Text {
            text: {
                if (toastType === "error") return "❌"
                if (toastType === "success") return "✅"
                if (toastType === "warning") return "⚠️"
                return "ℹ️"
            }
            font.pixelSize: 14
        }

        Text {
            id: toastTitle
            font.bold: true
            font.pixelSize: 13
            color: "#ffffff"
        }

        Text {
            id: toastMsg
            font.pixelSize: 13
            color: "#e2e8f0"
        }
    }

    Timer {
        id: dismissTimer
        onTriggered: toastRoot.opacity = 0.0
    }

    function show(type, title, message, duration_ms) {
        toastType = type || "info"
        toastTitle.text = title || ""
        toastMsg.text = message || ""
        toastRoot.opacity = 1.0
        dismissTimer.interval = duration_ms > 0 ? duration_ms : 3000
        dismissTimer.restart()
    }
}
