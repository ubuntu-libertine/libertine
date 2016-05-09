/**
 * @file ExtraArchiveView.qml
 * @brief Libertine container add archive view
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

Page {
    id: extraArchiveView
    header: PageHeader {
        id: pageHeader
        title: i18n.tr("Additional Archives and PPAs")
        trailingActionBar.actions: [
            Action {
                iconName: "add"
                text: i18n.tr("add")
                description: i18n.tr("Add a new PPA")
                onTriggered: PopupUtils.open(addArchivePopup)
            }
        ]
    }
    property var archive_name: null
    property var worker: null

    Component {
        id: addArchivePopup
        Dialog {
            id: addArchiveDialog
            title: i18n.tr("Add additional PPA")
            text: i18n.tr("Enter name of PPA in the form ppa:user/ppa-name:")

            TextField {
                id: extraArchiveString
                onAccepted: {
                    PopupUtils.close(addArchiveDialog)
                    addArchive(text)
                }
            }
            Button {
                text: i18n.tr("OK")
                color: UbuntuColors.green
                onClicked: {
                    PopupUtils.close(addArchiveDialog)
                    addArchive(extraArchiveString.text)
                }
            }
            Button {
                text: i18n.tr("Cancel")
                color: UbuntuColors.red
                onClicked: PopupUtils.close(addArchiveDialog)
            }
            Component.onCompleted: {
                extraArchiveString.forceActiveFocus()
            }
        }
    }

    UbuntuListView {
        id: extraArchiveList
        anchors {
            topMargin: pageHeader.height
            fill: parent
        }
        visible: !containerArchivesList.empty() ? true : false
        model: containerArchivesList
        delegate: ListItem {
            Label {
                anchors {
                    verticalCenter: parent.verticalCenter
                    left: parent.left
                    leftMargin: units.gu(2)
                }
                text: archiveName
            }
            ActivityIndicator {
                id: extraArchiveActivity
                anchors {
                    verticalCenter: parent.verticalCenter
                    right: parent.right
                    rightMargin: units.gu(2)
                }
                visible: (archiveStatus === i18n.tr("installing") ||
                          archiveStatus === i18n.tr("removing")) ? true : false
                running: extraArchiveActivity.visible
            }
            leadingActions: ListItemActions {
                actions: [
                    Action {
                        iconName: "delete"
                        text: i18n.tr("remove")
                        description: i18n.tr("Remove extra archive")
                        onTriggered: {
                            deleteArchive(archiveName)
                        }
                    }
                ]
            }
        }
    }

     Label {
        id: emptyLabel
        anchors.centerIn: parent
        visible: !extraArchiveList.visible  ? true : false
        wrapMode: Text.Wrap
        width: parent.width
        horizontalAlignment: Text.AlignHCenter
        text: i18n.tr("No additional archives and PPA's have been added")
    }

    function addArchive(archive) {
        var comp = Qt.createComponent("ContainerManager.qml")
        worker = comp.createObject(mainView, {"containerAction": ContainerManagerWorker.Configure,
                                              "containerId": mainView.currentContainer,
                                              "containerType": containerConfigList.getContainerType(mainView.currentContainer),
                                              "data_list": ["--add-archive", archive]})
        worker.finishedConfigure.connect(finishedConfigure)
        worker.start()
    }

    function deleteArchive(archive) {
        var comp = Qt.createComponent("ContainerManager.qml")
        worker = comp.createObject(mainView, {"containerAction": ContainerManagerWorker.Configure,
                                              "containerId": mainView.currentContainer,
                                              "containerType": containerConfigList.getContainerType(mainView.currentContainer),
                                              "data_list": ["--delete-archive", archive]})
        worker.finishedConfigure.connect(finishedConfigure)
        worker.start()
    }

    Component {
        id: addFailedPopup

        Dialog {
            property var error_msg: null
            id: addFailedDialog
            title: i18n.tr("Adding archive failed")
            text: error_msg

            Button {
                text: i18n.tr("Dismiss")
                onClicked: PopupUtils.close(addFailedDialog)
            }
        }
    }

    Component.onCompleted: {
        containerConfigList.configChanged.connect(reloadArchives)
    }

    Component.onDestruction: {
        containerConfigList.configChanged.disconnect(reloadArchives)

        if (worker) {
            worker.finishedConfigure.disconnect(finishedConfigure)
        }
    }

    function reloadArchives() {
        containerArchivesList.setContainerArchives(mainView.currentContainer)

        extraArchiveList.visible = !containerArchivesList.empty() ? true : false
    }

    function finishedConfigure(result, error_msg) {
        if (result) {
            containerArchivesList.setContainerArchives(mainView.currentContainer)
        }
        else {
            PopupUtils.open(addFailedPopup, null, {'error_msg': error_msg})
        }
    }  
}
