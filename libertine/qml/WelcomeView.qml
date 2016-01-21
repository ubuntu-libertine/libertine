/**
 * @file WelcomeView.qml
 * @brief Libertine default welcome view
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
import Libertine 1.0
import QtQuick 2.4
import QtQuick.Layouts 1.0
import Ubuntu.Components 1.2
import Ubuntu.Components.ListItems 1.0 as ListItem


Page {
    id: welcomeView
    title: i18n.tr("Welcome")

    function passwordAccepted(password) {
        var container_id = containerConfigList.addNewContainer("lxc")
        var comp = Qt.createComponent("ContainerManager.qml")
        var worker = comp.createObject(mainView, {"containerAction": ContainerManagerWorker.Create,
                                                  "containerId": container_id,
                                                  "containerType": "lxc",
                                                  "data": password})
        worker.containerDistro = containerConfigList.getContainerDistro(container_id)
        worker.containerName = containerConfigList.getContainerName(container_id)
        worker.start()
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

            text: i18n.tr("You do not have Legacy Application Support configured at" +
                          " this time.  Downloading and setting up the required" +
                          " environment takes some time and network bandwidth.")
        }

        Button {
            id: installButton
            Layout.alignment: Qt.AlignCenter
            Layout.maximumWidth: units.gu(12)

            text: i18n.tr("Install")
            color: UbuntuColors.green

            onClicked: {
                var item = pageStack.push(Qt.resolvedUrl("PasswordView.qml"))
                item.acceptPassword.connect(passwordAccepted)
            }

        }
    }

}
