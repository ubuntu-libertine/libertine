/**
 * @file ManageContainer.qml
 * @brief Libertine manage container view
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
import Ubuntu.Components 1.2
import Ubuntu.Components.ListItems 1.2 as ListItem


Page {
    id: manageView
    title: i18n.tr("Manage %1").arg(containerConfigList.getContainerName(mainView.currentContainer))

    Column {
        anchors.left: parent.left
        anchors.right: parent.right

        ListItem.Standard {
            visible: containerConfigList.getHostArchitecture() == 'x86_64' ? true : false
            control: CheckBox {
                checked: containerConfigList.getContainerMultiarchSupport(mainView.currentContainer) == 'enabled' ? true : false
                onClicked: {
                    var comp = Qt.createComponent("ContainerManager.qml")
                    if (checked) {
                        var worker = comp.createObject(mainView, {"containerAction": ContainerManagerWorker.Configure,
                                                                  "containerId": mainView.currentContainer,
                                                                  "containerType": containerConfigList.getContainerType(mainView.currentContainer),
                                                                  "data_list": ["--multiarch", "enable"]})
                        worker.start()
                    }
                    else {
                        var worker = comp.createObject(mainView, {"containerAction": ContainerManagerWorker.Configure,
                                                                  "containerId": mainView.currentContainer,
                                                                  "containerType": containerConfigList.getContainerType(mainView.currentContainer),
                                                                  "data_list": ["--multiarch", "disable"]})
                        worker.start()
                   }
                }
            }
            text: i18n.tr("i386 multiarch support")
        }

        ListItem.SingleValue {
            text: i18n.tr("Additional archives and PPAs")
            progression: true
            onClicked: {
                containerArchivesList.setContainerArchives(mainView.currentContainer)
                pageStack.push(Qt.resolvedUrl("ExtraArchivesView.qml"))
            }
        }

        ListItem.Standard {
            control: Button {
                id: updateButton
                text: i18n.tr("Update…")
                visible: (containerConfigList.getContainerStatus(mainView.currentContainer) === i18n.tr("ready")) ? true : false
                onClicked: {
                    updateContainer()
                }
            }
            ActivityIndicator {
                id: updateActivity
                anchors {
                    verticalCenter: parent.verticalCenter
                    right: parent.right
                    rightMargin: units.gu(2)
                }
                visible: (containerConfigList.getContainerStatus(mainView.currentContainer) === i18n.tr("updating")) ? true : false
                running: updateActivity.visible
            }
            text: i18n.tr("Update container")
        }   
    }

    Component.onCompleted: {
        containerConfigList.configChanged.connect(updateStatus)
    }

    Component.onDestruction: {
        containerConfigList.configChanged.disconnect(updateStatus)
    }

    function updateContainer() {
        var comp = Qt.createComponent("ContainerManager.qml")
        var worker = comp.createObject(mainView, {"containerAction": ContainerManagerWorker.Update,
                                                  "containerId": mainView.currentContainer,
                                                  "containerType": containerConfigList.getContainerType(mainView.currentContainer)})
        worker.start()
    }

    function updateStatus() {
        if (containerConfigList.getContainerStatus(mainView.currentContainer) === i18n.tr("updating")) {
            updateButton.visible = false
            updateActivity.visible = true
        }
        else if (containerConfigList.getContainerStatus(mainView.currentContainer) === i18n.tr("ready")) {
            updateButton.visible = true
            updateActivity.visible = false
        }
    }
}
