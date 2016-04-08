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
import Ubuntu.Components 1.2
import Ubuntu.Components.ListItems 1.2 as ListItem


Page {
    id: containerInfoView
    title: i18n.tr("Container information for %1").arg(mainView.currentContainer)
    property string currentContainer: mainView.currentContainer
    property string containerDistroText: containerConfigList.getContainerDistro(currentContainer)
    property string containerNameText: containerConfigList.getContainerName(currentContainer)
    property string containerIdText: currentContainer
    property var statusText: containerConfigList.getContainerStatus(currentContainer)

    Flickable {
        anchors.fill: parent
        contentHeight: contentItem.childrenRect.height
        boundsBehavior: (contentHeight > containerInfoView.height) ?
                            Flickable.DragAndOvershootBounds :
                            Flickable.StopAtBounds
        flickableDirection: Flickable.VerticalFlick

        Column {
            anchors.left: parent.left
            anchors.right: parent.right

            ListItem.Standard {
                text: i18n.tr("ID")
                control: Label {
                    text: containerIdText
                }
            }

            ListItem.Standard {
                text: i18n.tr("Name")
                control: Label {
                    text: containerNameText
                }
            }

            ListItem.Standard {
                text: i18n.tr("Distribution")
                control: Label {
                    text: containerDistroText
                }
            }

            ListItem.Standard {
                text: i18n.tr("Status")
                control: Label {
                    text: statusText
                }
            }
        }
    }

    Component.onCompleted: {
        containerConfigList.configChanged.connect(reloadStatus)
    }

    Component.onDestruction: {
        containerConfigList.configChanged.disconnect(reloadStatus)
    }

    function reloadStatus() {
        statusText = containerConfigList.getContainerStatus(currentContainer)
        if (!statusText) {
            statusText = i18n.tr("removed")
        }
    }
}
