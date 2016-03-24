/**
 * @file ConfigureContainer.qml
 * @brief Libertine configure container view
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
    id: configureView
    title: i18n.tr("Configure %1").arg(mainView.currentContainer)

    Column {
        anchors.left: parent.left
        anchors.right: parent.right

        ListItem.Standard {
            visible: containerConfigList.getHostArchitecture() == 'x86_64' ? true : false
            control: CheckBox {
                checked: containerConfigList.getContainerMultiarchSupport(mainView.currentContainer) == 'enabled' ? true : false
                onClicked: {
                    var comp = Qt.createComponent("ContainerManager.qml")
                    if (multiarchCheckBox.checked) {
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
    }
}
