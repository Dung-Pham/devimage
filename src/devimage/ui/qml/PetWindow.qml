import QtQuick
import QtQuick.Controls
import QtQuick.Window

Window {
    id: petWindow
    width: 230
    height: 300
    visible: true
    color: "transparent"
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool

    property bool chatOpen: false
    property string bubbleText: petController.configured
        ? "Chào bạn! Bấm vào mình để trò chuyện nhé 🐾"
        : "Mình đã sẵn sàng 🐾\nCần OPENAI_API_KEY để nói chuyện với bạn."

    function say(text) {
        bubbleText = text
        bubbleTimer.restart()
    }

    Timer {
        id: bubbleTimer
        interval: 7000
        onTriggered: bubbleText = petController.configured
            ? "Mình đang ở đây nếu bạn cần 🐾"
            : "Đặt OPENAI_API_KEY để bật AI nhé."
    }

    Rectangle {
        id: bubble
        visible: !petWindow.chatOpen
        width: Math.min(210, petWindow.width - 18)
        height: Math.max(54, bubbleLabel.implicitHeight + 24)
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        radius: 16
        color: "#f8fafc"
        border.color: "#dbe4ef"
        opacity: 0.97

        Text {
            id: bubbleLabel
            anchors.fill: parent
            anchors.margins: 12
            text: petWindow.bubbleText
            color: "#172033"
            font.pixelSize: 12
            wrapMode: Text.WordWrap
            verticalAlignment: Text.AlignVCenter
        }
    }

    Item {
        id: pet
        width: 170
        height: 180
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            drag.target: petWindow
            onClicked: petWindow.chatOpen = !petWindow.chatOpen
        }

        Rectangle {
            id: shadow
            width: 118
            height: 22
            radius: 11
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            color: "#20000000"
        }

        Rectangle {
            id: body
            width: 112
            height: 104
            radius: 50
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: shadow.top
            anchors.bottomMargin: 5
            color: "#9be7c8"
            border.color: "#4cae89"
            border.width: 3

            Behavior on y { NumberAnimation { duration: 500; easing.type: Easing.InOutQuad } }
            y: petController.busy ? -7 : 0

            Rectangle {
                width: 28; height: 38; radius: 8
                rotation: -25
                anchors.left: parent.left; anchors.leftMargin: 10
                anchors.top: parent.top; anchors.topMargin: -13
                color: parent.color; border.color: parent.border.color; border.width: 3
            }
            Rectangle {
                width: 28; height: 38; radius: 8
                rotation: 25
                anchors.right: parent.right; anchors.rightMargin: 10
                anchors.top: parent.top; anchors.topMargin: -13
                color: parent.color; border.color: parent.border.color; border.width: 3
            }

            Rectangle {
                width: 13; height: 18; radius: 7
                anchors.left: parent.left; anchors.leftMargin: 31
                anchors.top: parent.top; anchors.topMargin: 39
                color: "#243746"
                SequentialAnimation on height {
                    loops: Animation.Infinite
                    PauseAnimation { duration: 2600 }
                    NumberAnimation { to: 3; duration: 90 }
                    NumberAnimation { to: 18; duration: 90 }
                }
            }
            Rectangle {
                width: 13; height: 18; radius: 7
                anchors.right: parent.right; anchors.rightMargin: 31
                anchors.top: parent.top; anchors.topMargin: 39
                color: "#243746"
            }
            Rectangle {
                width: 12; height: 8; radius: 6
                anchors.centerIn: parent
                anchors.verticalCenterOffset: 15
                color: "#e98591"
            }
        }

        Rectangle {
            width: 18; height: 42; radius: 9
            anchors.right: body.right; anchors.rightMargin: -13
            anchors.verticalCenter: body.verticalCenter
            rotation: 35
            color: "#9be7c8"
            border.color: "#4cae89"; border.width: 3
            transformOrigin: Item.Bottom
            RotationAnimation on rotation { from: 25; to: 55; duration: 650; loops: Animation.Infinite; easing.type: Easing.InOutSine }
        }
    }

    Rectangle {
        id: chatPanel
        visible: petWindow.chatOpen
        width: 224
        height: 250
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        radius: 18
        color: "#f8fafc"
        border.color: "#cbd5e1"

        Column {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 8

            Row {
                width: parent.width
                spacing: 8
                Text { text: "🐾 Mimi"; font.bold: true; font.pixelSize: 15; color: "#172033" }
                Item { width: 1; height: 1 }
                Button {
                    text: "×"
                    width: 30; height: 28
                    anchors.right: parent.right
                    onClicked: petWindow.chatOpen = false
                }
            }

            Rectangle {
                width: parent.width
                height: 108
                radius: 12
                color: "#eef5f2"
                Text {
                    anchors.fill: parent
                    anchors.margins: 10
                    text: petWindow.bubbleText
                    color: "#263238"
                    font.pixelSize: 12
                    wrapMode: Text.WordWrap
                    verticalAlignment: Text.AlignVCenter
                }
            }

            TextField {
                id: input
                width: parent.width
                placeholderText: "Nói gì với Mimi..."
                enabled: !petController.busy
                onAccepted: sendButton.clicked()
            }

            Button {
                id: sendButton
                width: parent.width
                text: petController.busy ? "Mimi đang nghĩ..." : "Gửi"
                enabled: !petController.busy && input.text.trim().length > 0
                onClicked: {
                    var message = input.text.trim()
                    input.clear()
                    petController.ask(message)
                }
            }
        }
    }

    Connections {
        target: petController
        function onReplyReceived(reply) {
            petWindow.say(reply)
        }
        function onErrorOccurred(message) {
            petWindow.say(message)
        }
    }
}

