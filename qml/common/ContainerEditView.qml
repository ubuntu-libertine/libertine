/**
 * @file HomeView.qml
 * @brief Libertine container apps view
 */
/*
 * Copyright 2015-2017 Canonical Ltd
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
    clip: true
    header: PageHeader {
        id: pageHeader
        title: i18n.tr("%1 - All Apps").arg(containerConfigList.getContainerName(currentContainer))
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
                inputMethodHints: Qt.ImhNoAutoUppercase | Qt.ImhPreferLowercase | Qt.ImhNoPredictiveText
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
                    pageStack.addPageToNextColumn(homeView, Qt.resolvedUrl("ManageContainer.qml"), {currentContainer: currentContainer})
                }
            }
            Button {
                text: i18n.tr("Container Information")
                onTriggered: {
                    PopupUtils.close(settingsDialog)
                    pageStack.addPageToNextColumn(homeView, Qt.resolvedUrl("ContainerInfoView.qml"), {currentContainer: currentContainer})
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
                    pageStack.addPageToNextColumn(homeView, Qt.resolvedUrl("DebianPackagePicker.qml"), {packageList: packages})
                }
            }
            Button {
                text: i18n.tr("Search archives for a package")
                width: parent.width
                onClicked: {
                    PopupUtils.close(addAppsDialog)
                    openSearchDialog(currentContainer)
                }
            }
        }
    }

    property var searchResultsView: null
    function openSearchDialog(container) {
        var dialog = PopupUtils.open(Qt.resolvedUrl("SearchPackagesDialog.qml"), null, {currentContainer: container})
        dialog.initializeSearch.connect(function(query, container) {
            if (searchResultsView) {
                pageStack.removePages(searchResultsView)
                searchResultsView.destroy()
            }

            searchResultsView = Qt.createComponent("SearchResultsView.qml").createObject(homeView, {currentContainer: container, query: query})
            searchResultsView.newSearch.connect(openSearchDialog)

            pageStack.addPageToNextColumn(homeView, searchResultsView)
        })
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
        visible: !containerAppsList.empty()

        function info(packageName) {
            pageStack.addPageToNextColumn(homeView, Qt.resolvedUrl("PackageInfoView.qml"), {"currentPackage": packageName, "currentContainer": currentContainer})
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
        var worker = Qt.createComponent("ContainerManager.qml").createObject(parent)
        worker.error.connect(containerOperationDetails.error)
        worker.updateOperationDetails.connect(containerOperationDetails.update)
        containerOperationDetails.send.connect(worker.containerOperationInteraction)
        worker.operationFinished.connect(containerOperationDetails.clear)
        return worker
    }

    function installPackage(packageName) {
        operationSetup().installPackage(currentContainer, packageName)
    }

    function removePackage(packageName) {
        operationSetup().removePackage(currentContainer, packageName)
    }
}
