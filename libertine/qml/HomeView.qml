/**
 * @file HomeView.qml
 * @brief Libertine container apps view
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
import Ubuntu.Components 1.2
import Ubuntu.Components.Popups 1.0


Page {
    id: homeView
    title: i18n.tr("Classic Apps") + " - " + mainView.currentContainer

    head.actions: [
        Action {
	    iconName: "add"
	    onTriggered: pageStack.push(Qt.resolvedUrl("AppAddView.qml"))
	},
        Action {
	    id: settingsButton
	    iconName: "settings"
	    onTriggered: PopupUtils.open(settingsMenu, homeView)
	}
    ]

    Component {
	id: settingsMenu
	ActionSelectionPopover {
	    actions: ActionList {
		Action {
		    text: "App Sources"
		    onTriggered: print(text)
		}
                Action {
                    text: "Update Container"
                    onTriggered: {
                        updateContainer()
                    }
                }
		Action {
		    text: "Switch Container"
		    onTriggered: {
                        pageStack.pop()
                        pageStack.push(Qt.resolvedUrl("ContainersView.qml"))
                    }
		}
	    }
	}
    }

    UbuntuListView {
        anchors.fill: parent
        model: containerAppsList
        delegate: ListItem {
            Label {
                text: packageName
            }
            leadingActions: ListItemActions {
                actions: [
                    Action {
                        iconName: "delete"
                        text: i18n.tr("delete")
                        description: i18n.tr("Remove Package")
                        onTriggered: {
                            removePackage(packageName)
                            containerAppsList.removeApp(mainView.currentContainer, packageName)
                        }
                    }
                ]
            }
            trailingActions: ListItemActions {
                actions: [
                    Action {
                        iconName: "info"
                        text: i18n.tr("info")
                        description: i18n.tr("Package Info")
                        onTriggered: {
                            console.log("info for package " + packageName)
                        }
                    }
                ]
            }
        }
    }

    function updateContainer() {
        var comp = Qt.createComponent("ContainerManager.qml")
        var worker = comp.createObject()
        worker.containerAction = ContainerManagerWorker.Update
        worker.containerId = mainView.currentContainer
        worker.start()
    }

    function removePackage(packageName) {
        var comp = Qt.createComponent("ContainerManager.qml")
        var worker = comp.createObject()
        worker.containerAction = ContainerManagerWorker.Remove
        worker.containerId = mainView.currentContainer
        worker.data = packageName
        worker.start()
    }
}
