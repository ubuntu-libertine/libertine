/**
 * @file HomeView.qml
 * @brief Libertine container apps view
 */
/*
 * Copyright 2015-2016 Canonical Ltd
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
    id: homeView
    header: PageHeader {
        id: pageHeader
        title: i18n.tr("Classic Apps - %1").arg(containerConfigList.getContainerName(currentContainer))
        trailingActionBar.actions: [
            Action {
                id: settingsButton
                iconName: "settings"
                onTriggered: PopupUtils.open(settingsMenu)
            },
            Action {
                iconName: "add"
                onTriggered: PopupUtils.open(addAppsMenu)
            }
        ]
    }
    property string currentContainer: null

    Component {
        id: enterPackagePopup
        Dialog {
            id: enterPackageDialog
            title: i18n.tr("Install new package")
            text: i18n.tr("Enter exact package name or full path to a Debian package file")

            Label {
                id: appExistsWarning
                wrapMode: Text.Wrap
                visible: false
            }

            TextField {
                id: enterPackageInput
                placeholderText: i18n.tr("Package name or Debian package path")
                onAccepted: okButton.clicked()
            }

            Row {
                spacing: units.gu(1)

                Button {
                    id: okButton
                    text: i18n.tr("OK")
                    color: UbuntuColors.green
                    width: (parent.width - parent.spacing) / 2
                    onClicked: {
                        if (enterPackageInput.text != "") {
                            if (!containerConfigList.isAppInstalled(currentContainer, enterPackageInput.text)) {
                                installPackage(enterPackageInput.text)
                                PopupUtils.close(enterPackageDialog)
                            }
                            else {
                                appExistsWarning.text = i18n.tr("The %1 package is already installed. Please try a different package name.").arg(enterPackageInput.text)
                                appExistsWarning.visible = true
                                enterPackageInput.text = "" 
                            }
                        }
                    }
                }

                Button {
                    id: cancelButton
                    text: i18n.tr("Cancel")
                    color: UbuntuColors.red
                    width: (parent.width - parent.spacing) / 2
                    onClicked: PopupUtils.close(enterPackageDialog)
                }
            }

            Component.onCompleted: enterPackageInput.forceActiveFocus()
        }
    }

    Component {
        id: settingsMenu
        Dialog {
            id: settingsDialog
            __closeOnDismissAreaPress: true
            Button {
                text: i18n.tr("Manage Container")
                onTriggered: {
                    PopupUtils.close(settingsDialog)
                    pageStack.push(Qt.resolvedUrl("ManageContainer.qml"), {currentContainer: currentContainer})
                }
            }
            Button {
                text: i18n.tr("Container Information")
                onTriggered: {
                    PopupUtils.close(settingsDialog)
                    pageStack.push(Qt.resolvedUrl("ContainerInfoView.qml"), {currentContainer: currentContainer})
                }
            }
            Button {
                text: i18n.tr("Switch Container")
                onTriggered: {
                    PopupUtils.close(settingsDialog)
                    pageStack.pop()
                }
            }
        }
    }

    Component {
        id: addAppsMenu
        Dialog {
            id: addAppsDialog
            __closeOnDismissAreaPress: true

            Button {
                text: i18n.tr("Enter package name or Debian file")
                width: parent.width
                onClicked: {
                    PopupUtils.close(addAppsDialog)
                    PopupUtils.open(enterPackagePopup)
                }
            }
            Button {
                text: i18n.tr("Choose Debian package to install")
                width: parent.width
                onClicked: {
                    PopupUtils.close(addAppsDialog)
                    var packages = containerConfigList.getDebianPackageFiles()
                    pageStack.push(Qt.resolvedUrl("DebianPackagePicker.qml"), {packageList: packages})
                }
            }
            Button {
                text: i18n.tr("Search archives for a package")
                width: parent.width
                onClicked: {
                    PopupUtils.close(addAppsDialog)
                    PopupUtils.open(Qt.resolvedUrl("SearchPackagesDialog.qml"))
                }
            }
        }
    }

    Component.onCompleted: {
        containerConfigList.configChanged.connect(reloadAppList)
    }

    Component.onDestruction: {
        containerConfigList.configChanged.disconnect(reloadAppList)
    }

    function reloadAppList() {
        containerAppsList.setContainerApps(currentContainer)

        appsList.visible = !containerAppsList.empty()  ? true : false
    }

    UbuntuListView {
        id: appsList
        anchors {
            topMargin: pageHeader.height
            fill: parent
        }
        model: containerAppsList
        visible: !containerAppsList.empty()  ? true : false

        function info(packageName) {
            pageStack.push(Qt.resolvedUrl("PackageInfoView.qml"), {"currentPackage": packageName, "currentContainer": currentContainer})
        }

        delegate: ListItem {
            Label {
                text: packageName
                anchors {
                    verticalCenter: parent.verticalCenter
                    left: parent.left
                    leftMargin: units.gu(2)
                }
            }
            ActivityIndicator {
                id: appActivity
                anchors {
                    verticalCenter: parent.verticalCenter
                    right: parent.right
                    rightMargin: units.gu(2)
                }
                visible: (appStatus === i18n.tr("installing") ||
                          appStatus === i18n.tr("removing")) ? true : false
                running: appActivity.visible
            }

            onClicked: {
                appsList.info(packageName);
            }

            leadingActions: ListItemActions {
                actions: [
                    Action {
                        iconName: "delete"
                        text: i18n.tr("delete")
                        description: i18n.tr("Remove Package")
                        onTriggered: {
                            removePackage(packageName)
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
                            appsList.info(packageName)
                        }
                    }
                ]
            }
        }
    }

    Label {
        id: emptyLabel
        anchors.centerIn: parent
        visible: !appsList.visible
        wrapMode: Text.Wrap
        width: parent.width
        horizontalAlignment: Text.AlignHCenter
        text: i18n.tr("No packages are installed")
    }

    function operationSetup() {
        var comp = Qt.createComponent("ContainerManager.qml")
        var worker = comp.createObject(mainView)
        worker.error.connect(mainView.error)
        worker.updateOperationDetails.connect(mainView.updateOperationDetails)
        mainView.packageOperationInteraction.connect(worker.packageOperationInteraction)
        worker.operationFinished.connect(mainView.resetOperationDetails)
        return worker
    }

    function installPackage(packageName) {
        operationSetup().installPackage(currentContainer, packageName)
    }

    function removePackage(packageName) {
        operationSetup().removePackage(currentContainer, packageName)
    }
}
