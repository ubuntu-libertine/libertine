/**
 * @file ContainerInfoView.qml
 * @brief Container info view
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
import QtQuick.Layouts 1.0
import Ubuntu.Components 1.3
import Ubuntu.Components.ListItems 1.3 as ListItem


Page {
    id: containerInfoView
    header: PageHeader {
        id: pageHeader
        title: i18n.tr("Container Info: %1").arg(containerConfigList.getContainerName(currentContainer))
    }

    property string currentContainer: null
    property string containerDistroText: containerConfigList.getContainerDistro(currentContainer)
    property string containerNameText: containerConfigList.getContainerName(currentContainer)
    property string containerIdText: currentContainer
    property var statusText: containerConfigList.getContainerStatus(currentContainer)
    property bool showDetails: false
    property string operationDetails: ""

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
                id: idView
                text: i18n.tr("ID")
                control: Label {
                    text: containerIdText
                }
            }

            ListItem.Standard {
                id: nameView
                text: i18n.tr("Name")
                control: Label {
                    text: containerNameText
                }
            }

            ListItem.Standard {
                id: distroView
                text: i18n.tr("Distribution")
                control: Label {
                    text: containerDistroText
                }
            }

            ListItem.Standard {
                id: statusView
                text: i18n.tr("Status")
                control: Label {
                    text: statusText
                }
            }

            ListItem.Standard {
                id: showDetailsView
                control: Button {
                    text: enabled ?
                              showDetails ? i18n.tr('Hide') : i18n.tr('Show')
                            : i18n.tr('None')
                    enabled: operationDetails != ""
                    onClicked: {
                        showDetails = !showDetails
                    }
                }
                text: i18n.tr("Operation details")
            }

            TextArea {
                id: operationDetailsView
                visible: showDetails
                anchors.left: parent.left
                anchors.right: parent.right
                height: Math.max(containerInfoView.height - pageHeader.height - idView.height - nameView.height - distroView.height
                                                          - statusView.height - showDetailsView.height,
                                 units.gu(35))
                readOnly: true
                text: operationDetails
            }
        }
    }

    Component.onCompleted: {
        containerConfigList.configChanged.connect(reloadStatus)

        var worker = Qt.createComponent("ContainerManager.qml").createObject(parent)
        operationDetails = packageOperationDetails.details(currentContainer, "")
        packageOperationDetails.updated.connect(updateDetails)

        operationDetailsView.cursorPosition = operationDetailsView.length
        if (operationDetails !== "") {
            showDetails = !showDetails
        }
    }

    Component.onDestruction: {
        containerConfigList.configChanged.disconnect(reloadStatus)
    }

    function updateDetails(container_id, package_name, details) {
        if (container_id === currentContainer && package_name === "") {
            operationDetails += details
            operationDetailsView.cursorPosition = operationDetailsView.length
        }
    }

    function reloadStatus() {
        statusText = containerConfigList.getContainerStatus(currentContainer)
        if (!statusText) {
            statusText = i18n.tr("removed")
        }
    }
}
