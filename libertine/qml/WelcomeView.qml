/**
 * @file WelcomeView.qml
 * @brief Libertine default welcome view
 */
/*
 * Copyright 2015-2016 Canonical Ltd
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
import Ubuntu.Components 1.3
import Ubuntu.Components.Popups 1.3


Page {
    id: welcomeView
    header: PageHeader {
        title: i18n.tr("Welcome")
        leadingActionBar.actions: [
            Action {
                iconName: "back"
                visible: false
            }
        ]
    }

    ColumnLayout {
        spacing: units.gu(2)
        anchors {
            fill: parent
            margins: units.gu(4)
        }

        Label {
            id: welcomeMessage
            Layout.fillWidth: true
            wrapMode: Text.Wrap
            horizontalAlignment: Text.AlignHCenter

            text: i18n.tr("Welcome to the Ubuntu Legacy Application Support Manager.")
        }
        Label {
            id: warningMessage
            Layout.fillWidth: true
            wrapMode: Text.Wrap
            horizontalAlignment: Text.AlignHCenter

            text: i18n.tr("You do not have Legacy Application Support configured at this time.  Downloading and setting up the required environment takes some time and network bandwidth.")
        }

        Button {
            id: installButton
            Layout.alignment: Qt.AlignCenter
            Layout.maximumWidth: units.gu(12)

            text: i18n.tr("Install")
            color: UbuntuColors.green

            onClicked: {
                PopupUtils.open(Qt.resolvedUrl("ContainerOptionsDialog.qml"))
            }
        }
    }

    function showPasswordDialog(enableMultiarch, containerName) {
        PopupUtils.open(Qt.resolvedUrl("ContainerPasswordDialog.qml"), null, {"enableMultiarch": enableMultiarch, "containerName": containerName})
    }
}
