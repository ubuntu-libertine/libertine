/*
 * Copyright 2017 Canonical Ltd
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

Page {
    id: extraBindMountsView
    clip: true
    header: PageHeader {
        id: pageHeader
        title: i18n.tr("Mapped Directories")
        trailingActionBar.actions: [
            Action {
                iconName: "add"
                text: i18n.tr("add")
                description: i18n.tr("Add a new bind-mount")
                onTriggered: {
                    var fileDialog = Qt.createComponent("AddBindMountDialog.qml").createObject(extraBindMountsView)
                    fileDialog.open()
                }
            }
        ]
    }
    property string currentContainer: ""

    signal error(string description, string details)

    UbuntuListView {
        id: bindMountsListView
        anchors {
            topMargin: pageHeader.height
            fill: parent
        }
        model: containerBindMountsList
        visible: !containerBindMountsList.empty()
        delegate: ListItem {
            Label {
                anchors {
                    verticalCenter: parent.verticalCenter
                    left: parent.left
                    leftMargin: units.gu(2)
                }
                text: path
                width: parent.width - units.gu(8)
                elide: Text.ElideMiddle
            }
            leadingActions: ListItemActions {
                actions: [
                    Action {
                        iconName: "delete"
                        text: i18n.tr("remove")
                        description: i18n.tr("Remove mapped directory")
                        onTriggered: {
                            deleteBindMount(path)
                        }
                    }
                ]
            }
        }
    }

     Label {
        id: emptyLabel
        anchors.centerIn: parent
        visible: !bindMountsListView.visible
        wrapMode: Text.Wrap
        width: parent.width
        horizontalAlignment: Text.AlignHCenter
        text: i18n.tr("No custom bind-mounts have been added to this container.\n" +
                      "Adding a directory here will allow you to modify its contents within this container.")
    }

    function deleteBindMount(mount) {
        var worker = Qt.createComponent("ContainerManager.qml").createObject(mainView)
        worker.error.connect(containerOperationDetails.error)
        worker.configureContainer(currentContainer, containerConfigList.getContainerName(currentContainer), ["--bind-mount", "remove", "--mount-path", "\"" + mount + "\""])
    }

    function addBindMount(mount) {
        var worker = Qt.createComponent("ContainerManager.qml").createObject(mainView)
        worker.error.connect(containerOperationDetails.error)
        worker.configureContainer(currentContainer, containerConfigList.getContainerName(currentContainer), ["--bind-mount", "add", "--mount-path", "\"" + mount + "\""])
    }

    Component.onCompleted: {
        containerConfigList.configChanged.connect(reloadMounts)
    }

    Component.onDestruction: {
        containerConfigList.configChanged.disconnect(reloadMounts)
    }

    function reloadMounts() {
        containerBindMountsList.setContainerBindMounts(currentContainer)
        bindMountsListView.visible = !containerBindMountsList.empty()
    }
}
