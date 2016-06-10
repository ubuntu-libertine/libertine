/**
 * @file ContainerPasswordDialog.qml
 * @brief Libertine container password dialog
 */
/*
 * Copyright 2016 Canonical Ltd
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
import Libertine 1.0
import QtQuick 2.4
import Ubuntu.Components 1.3
import Ubuntu.Components.Popups 1.3


Dialog {
    id: passwordDialog
    title: i18n.tr("Authentication required")
    text: i18n.tr("Password is required to create a Libertine container")
    property var enableMultiarch: false
    property var containerName: null
    property var switchPage: false

    Label {
        id: invalidPasswordText
        visible: false
        text: i18n.tr("Invalid password entered")
    }

    TextField {
        id: passwordInput
        placeholderText: i18n.tr("password")
        echoMode: TextInput.Password

        onAccepted: okButton.clicked()
    }

    Row {
        spacing: units.gu(1)

        Button {
            id: okButton
            text: i18n.tr("OK")
            color: UbuntuColors.green
            width: (parent.width - parent.spacing) / 2
            onClicked: {
                if (passwordHelper.VerifyUserPassword(passwordInput.text)) {
                    passwordAccepted(text)
                    switchPage = true
                    PopupUtils.close(passwordDialog)
                }
                else {
                    invalidPasswordText.visible = true
                }
                passwordInput.text = ""
            }
        }

        Button {
            id: cancelButton
            text: i18n.tr("Cancel")
            color: UbuntuColors.red
            width: (parent.width - parent.spacing) / 2
            onClicked: PopupUtils.close(passwordDialog)
        }
    }

    Component.onCompleted: passwordInput.forceActiveFocus()

    Component.onDestruction: {
        if (switchPage) {
            pageStack.clear()
            pageStack.push(Qt.resolvedUrl("ContainersView.qml"))
        }
    }

    function passwordAccepted(password) {
        var container_id = containerConfigList.addNewContainer("lxc", containerName)
        var comp = Qt.createComponent("ContainerManager.qml")
        var worker = comp.createObject(mainView)

        worker.updateOperationDetails.connect(mainView.updateOperationDetails)
        worker.operationFinished.connect(mainView.resetOperationDetails)
        worker.error.connect(mainView.error)

        worker.createContainer(container_id, containerConfigList.getContainerName(container_id),
                               containerConfigList.getContainerDistro(container_id), enableMultiarch, password)
    }
}
