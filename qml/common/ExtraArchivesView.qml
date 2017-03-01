/**
 * @file ExtraArchiveView.qml
 * @brief Libertine container extra archive view
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

Page {
    id: extraArchiveView
    clip: true
    header: PageHeader {
        id: pageHeader
        title: i18n.tr("Additional Archives")
        trailingActionBar.actions: [
            Action {
                iconName: "add"
                text: i18n.tr("add")
                description: i18n.tr("Add a new archive")
                onTriggered: pageStack.addPageToNextColumn(extraArchiveView, Qt.resolvedUrl("AddExtraArchiveView.qml"), {currentContainer: currentContainer})
            }
        ]
    }
    property string currentContainer: ""

    signal error(string description, string details)

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
                width: parent.width - units.gu(8)
                elide: Text.ElideMiddle
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

    function deleteArchive(archive) {
        var worker = Qt.createComponent("ContainerManager.qml").createObject(mainView)
        worker.finishedConfigure.connect(finishedConfigure)
        worker.error.connect(containerOperationDetails.error)
        worker.configureContainer(currentContainer, containerConfigList.getContainerName(currentContainer), ["--archive", "remove", "--archive-name", "\"" + archive + "\""])
    }

    Component.onCompleted: {
        containerConfigList.configChanged.connect(reloadArchives)
    }

    Component.onDestruction: {
        containerConfigList.configChanged.disconnect(reloadArchives)
    }

    function reloadArchives() {
        containerArchivesList.setContainerArchives(currentContainer)

        extraArchiveList.visible = !containerArchivesList.empty() ? true : false
    }

    function finishedConfigure() {
        if (extraArchiveView) {
            containerArchivesList.setContainerArchives(currentContainer)
        }
    }
}
