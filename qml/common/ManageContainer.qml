/**
 * @file ManageContainer.qml
 * @brief Libertine manage container view
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
import Ubuntu.Components.ListItems 1.3 as ListItem


Page {
    id: manageView
    header: PageHeader {
        id: pageHeader
        title: i18n.tr("Manage %1").arg(containerConfigList.getContainerName(currentContainer))
    }
    property bool isDefaultContainer: null
    property bool isMultiarchEnabled: null
    property bool showFreezeOption: false
    property bool freezeOnStop: null
    property string currentContainer: null

    Flickable {
        anchors {
            topMargin: pageHeader.height
            fill: parent
        }
        contentHeight: contentItem.childrenRect.height
        boundsBehavior: Flickable.DragAndOvershootBounds
        flickableDirection: Flickable.VerticalFlick

        Column {
            anchors.left: parent.left
            anchors.right: parent.right

            ListItem.Standard {
                visible: containerConfigList.getHostArchitecture() === 'x86_64' ? true : false
                control: CheckBox {
                    checked: isMultiarchEnabled
                    onClicked: {
                        var worker = Qt.createComponent("ContainerManager.qml").createObject(parent)

                        worker.updateOperationDetails.connect(containerOperationDetails.update)
                        worker.operationFinished.connect(containerOperationDetails.clear)

                        if (checked) {
                            worker.configureContainer(currentContainer,
                                                      containerConfigList.getContainerName(currentContainer),
                                                      ["--multiarch", "enable"])
                        } else {
                            worker.configureContainer(currentContainer,
                                                      containerConfigList.getContainerName(currentContainer),
                                                      ["--multiarch", "disable"])
                        }
                    }
                }
                text: i18n.tr("i386 multiarch support")
            }

            ListItem.Standard {
                visible: showFreezeOption
                control: CheckBox {
                    checked: freezeOnStop
                    onClicked: {
                        var worker = Qt.createComponent("ContainerManager.qml").createObject(parent)

                        worker.updateOperationDetails.connect(containerOperationDetails.update)
                        worker.operationFinished.connect(containerOperationDetails.clear)

                        if (checked) {
                            worker.configureContainer(currentContainer,
                                                      containerConfigList.getContainerName(currentContainer),
                                                      ["--freeze", "enable"])
                        } else {
                            worker.configureContainer(currentContainer,
                                                      containerConfigList.getContainerName(currentContainer),
                                                      ["--freeze", "disable"])
                        }
                    }
                }
                text: i18n.tr("Freeze on stop")
            }

            ListItem.SingleValue {
                text: i18n.tr("Additional archives and PPAs")
                progression: true
                onClicked: {
                    containerArchivesList.setContainerArchives(currentContainer)
                    pageStack.addPageToNextColumn(manageView, Qt.resolvedUrl("ExtraArchivesView.qml"), {currentContainer: currentContainer})
                }
            }

            ListItem.SingleValue {
                text: i18n.tr("Additional bind-mounts")
                progression: true
                onClicked: {
                    containerBindMountsList.setContainerBindMounts(currentContainer)
                    pageStack.addPageToNextColumn(manageView, Qt.resolvedUrl("ExtraBindMountsView.qml"), {currentContainer: currentContainer})
                }
            }

            ListItem.Standard {
                control: Button {
                    id: updateButton
                    text: i18n.tr("Update…")
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
                    visible: (containerConfigList.getContainerStatus(currentContainer) === i18n.tr("updating")) ? true : false
                    running: updateActivity.visible
                }
                text: i18n.tr("Update container")
            }

            ListItem.Standard {
                control: CheckBox {
                    checked: isDefaultContainer
                    onClicked: {
                        var worker = Qt.createComponent("ContainerManager.qml").createObject(parent)
                        worker.error.connect(containerOperationDetails.error)

                        var fallback = checked
                        worker.error.connect(function() {
                            checked = fallback
                        })

                        worker.setDefaultContainer(currentContainer, !checked)
                    }
                }
                text: i18n.tr("Default container")
            }
        }
    }

    Component.onCompleted: {
        updateContainerInfo()
        containerConfigList.configChanged.connect(updateContainerInfo)
    }

    Component.onDestruction: {
        containerConfigList.configChanged.disconnect(updateContainerInfo)
    }

    function updateContainer() {
        var worker = Qt.createComponent("ContainerManager.qml").createObject(parent)
        worker.error.connect(containerOperationDetails.error);

        worker.updateOperationDetails.connect(containerOperationDetails.update)
        worker.operationFinished.connect(containerOperationDetails.clear)

        worker.updateContainer(currentContainer, containerConfigList.getContainerName(currentContainer))
    }

    function updateContainerInfo() {
        updateStatus()
        isDefaultContainer = containerConfigList.defaultContainerId === currentContainer
        isMultiarchEnabled = containerConfigList.getContainerMultiarchSupport(currentContainer) === 'enabled'
        var containerType = containerConfigList.getContainerType(currentContainer)

        if (containerType === 'lxc' || containerType === 'lxd') {
            showFreezeOption = true
            freezeOnStop = containerConfigList.getFreezeOnStop(currentContainer)
        }
    }

    function updateStatus() {
        if (containerConfigList.getContainerStatus(currentContainer) === i18n.tr("updating")) {
            updateButton.visible = false
            updateActivity.visible = true
        }
        else if (containerConfigList.getContainerStatus(currentContainer) === i18n.tr("ready")) {
            updateButton.visible = true
            updateActivity.visible = false
        }
    }
}
