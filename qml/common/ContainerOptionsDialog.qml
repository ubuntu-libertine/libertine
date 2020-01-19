/**
 * @file ContainerOptionsDialog.qml
 * @brief Libertine container options dialog
 */
/*
 * Copyright 2016-2017 Canonical Ltd
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
import Ubuntu.Components.ListItems 1.3 as ListItem

Dialog {
    id: containerOptionsDialog
    title: i18n.tr("Container Options")
    text: i18n.tr("Configure options for container creation.")

    signal onCreateInitialized()

    Row {
        visible: containerConfigList.getHostArchitecture() === 'x86_64' ? true : false
        spacing: units.gu(1)
        CheckBox {
            id: enableMultiarchCheckbox
        }

        Label {
            id: enableMultiarchText
            text: i18n.tr("i386 multiarch support")
            anchors {
                leftMargin: units.gu(2)
                verticalCenter: enableMultiarchCheckbox.verticalCenter
            }
        }
    }

    Label {
        id: containerNameText
        text: i18n.tr("Enter a name for the container or leave blank for default name:")
        wrapMode: Text.Wrap
    }

    TextField {
        id: containerNameInput
        placeholderText: i18n.tr("container name")
        onAccepted: okButton.clicked()
    }

    Label {
        id: containerPasswordText
        visible: true
        text: i18n.tr("Enter password for your user in the Libertine container or leave blank for no password:")
        wrapMode: Text.Wrap
    }

    TextField {
        id: containerPasswordInput
        visible: containerPasswordText.visible
        placeholderText: i18n.tr("password")
        echoMode: TextInput.Password
    }

    Row {
        spacing: units.gu(1)

        Button {
            id: cancelButton
            text: i18n.tr("Cancel")
            width: (parent.width - parent.spacing) / 2
            onClicked: PopupUtils.close(containerOptionsDialog)
        }

        Button {
            id: okButton
            text: i18n.tr("OK")
            color: theme.palette.normal.positive
            width: (parent.width - parent.spacing) / 2
            onClicked: {
                createContainer()
                onCreateInitialized()
                PopupUtils.close(containerOptionsDialog)
            }
        }

    }

    function createContainer() {
        var container_id = containerConfigList.addNewContainer("lxc", containerNameInput.text)
        var worker = Qt.createComponent("ContainerManager.qml").createObject(parent)

        worker.updateOperationDetails.connect(containerOperationDetails.update)
        worker.operationFinished.connect(containerOperationDetails.clear)
        worker.error.connect(containerOperationDetails.error)

        worker.createContainer(container_id,
                               containerConfigList.getContainerName(container_id),
                               containerConfigList.getContainerDistro(container_id),
                               enableMultiarchCheckbox.checked,
                               containerPasswordInput.text)
    }
}
