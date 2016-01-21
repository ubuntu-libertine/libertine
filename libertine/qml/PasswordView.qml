/**
 * @file PasswordView.qml
 * @brief Libertine password view
 */
/*
 * Copyright 2015 Canonical Ltd
 *
 * Libertine is free software: you can redistribute it and/or modify it under
 * the terms of the GNU General Public License, version 3, as published by the
 * Free Software Foundation.
 *
 * Libertine is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
 * A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
import QtQuick 2.4
import QtQuick.Layouts 1.0
import Ubuntu.Components 1.2

Page {
    id: passwordView
    title: i18n.tr("Password")

    signal acceptPassword(string password)

    Label {
        id: infoLabel
        objectName: "infoLabel"
        Layout.fillWidth: true
        wrapMode: Text.Wrap
        horizontalAlignment: Text.AlignHCenter

        text: i18n.tr("Please enter the password for your user") + ":"
    }

    TextField {
        id: passwordInput
        objectName: "passwordInput"

        anchors {
            top: infoLabel.bottom
            horizontalCenter: parent.horizontalCenter
            margins: units.gu(1)
        }
        height: units.gu(4.5)
        width: parent.width - anchors.margins * 2

        echoMode: TextInput.Password

        onAccepted: {
            if (passwordHelper.VerifyUserPassword(text)) {
                passwordView.acceptPassword(text)
                pageStack.clear()
                pageStack.push(Qt.resolvedUrl("ContainersView.qml"))
            }
            text = ""
        }
    }

    Component.onCompleted: {
        passwordInput.forceActiveFocus()
    }
}
