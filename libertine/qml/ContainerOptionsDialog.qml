/**
 * @file ContainerOptionsDialog.qml
 * @brief Libertine container options dialog
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
import Ubuntu.Components.ListItems 1.3 as ListItem

Dialog {
    id: containerOptionsDialog
    title: i18n.tr("Container Options")
    text: i18n.tr("Configure options for container creation.")
    property var showPasswordDialog: false
    signal passwordDialogSignal(var enableMultiarch, var containerName)

    Row {
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
        text: i18n.tr("Enter or name for the container or leave blank for default name")
        wrapMode: Text.Wrap
    }

    TextField {
        id: containerNameInput
        placeholderText: i18n.tr("container name")
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
                showPasswordDialog = true
                PopupUtils.close(containerOptionsDialog)
            }
        }

        Button {
            id: cancelButton
            text: i18n.tr("Cancel")
            color: UbuntuColors.red
            width: (parent.width - parent.spacing) / 2
            onClicked: PopupUtils.close(containerOptionsDialog)
        }
    }

    Component.onDestruction: {
        if (showPasswordDialog) {
            passwordDialogSignal(enableMultiarchCheckbox.checked, containerNameInput.text)
        }
    }
}
