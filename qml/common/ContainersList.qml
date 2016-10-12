/**
 * @file ContainersListView.qml
 * @brief Libertine containers view
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


/**
 * Component providing a list of available containers and their (possibly animated)
 * states.
 */
Item {
    property string currentContainer

    UbuntuListView {
        id: containersList
        anchors {
            fill: parent
        }
        model: containerConfigList

        function edit(id, status) {
            if (status === "removing") {
                packageOperationDetails.error(i18n.tr("Container Unavailable"), i18n.tr("Container is being destroyed and is no longer editable."))
                return
            }
            currentContainer = id
            containerAppsList.setContainerApps(currentContainer)
            pageStack.push(Qt.resolvedUrl("../common/ContainerEditView.qml"), {currentContainer: currentContainer})
        }

        delegate: ListItem {
            Label {
                text: name
                anchors {
                    verticalCenter: parent.verticalCenter
                    left: parent.left
                    leftMargin: units.gu(2)
                }
            }
            ActivityIndicator {
                id: containerActivity
                anchors {
                    verticalCenter: parent.verticalCenter
                    right: parent.right
                    rightMargin: units.gu(2)
                }
                visible: installStatus === i18n.tr("installing") ||
                          installStatus === i18n.tr("removing")
                running: containerActivity.visible
            }

            onClicked: { containersList.edit(containerId, installStatus) }

            leadingActions: ListItemActions {
                actions: [
                    Action {
                        iconName: "delete"
                        text: i18n.tr("delete")
                        description: i18n.tr("Delete Container")
                        onTriggered: {
                            var worker = Qt.createComponent("../common/ContainerManager.qml").createObject(parent)
                            worker.error.connect(packageOperationDetails.error)
                            worker.destroyContainer(containerId)
                        }
                    }
                ]
            }

            trailingActions: ListItemActions {
                actions: [
                    Action {
                        iconName: "info"
                        text: i18n.tr("info")
                        description: i18n.tr("Container Info")
                        onTriggered: {
                            currentContainer = containerId
                            pageStack.push(Qt.resolvedUrl("../common/ContainerInfoView.qml"), {currentContainer: containerId})
                        }
                    },
                    Action {
                        iconName: "edit"
                        text: i18n.tr("edit")
                        description: i18n.tr("Container Apps")
                        visible: installStatus === i18n.tr("ready") ||
                                  installStatus === i18n.tr("updating")
                        onTriggered: {
                            containersList.edit(containerId, installStatus)
                        }
                    }
                ]
            }
        }
    }

    Component.onCompleted: {
        containerConfigList.configChanged.connect(updateContainerList)
    }

    Component.onDestruction: {
        containerConfigList.configChanged.disconnect(updateContainerList)
    }

    function updateContainerList() {
        containerConfigList.reloadContainerList()

        if (currentContainer && !containerConfigList.getContainerStatus(currentContainer) && pageStack.currentPage !== containersView) {
            pageStack.pop()
            currentContainer = ""
            packageOperationDetails.error(i18n.tr("Container Unavailable"),
                                          i18n.tr("This container has been destroyed and is no longer valid. You have been returned to the containers overview."))
        }
    }
}
