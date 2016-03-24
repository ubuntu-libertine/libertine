/**
 * @file AppAddView.qml
 * @brief Libertine app add view
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
import QtQuick.Layouts 1.1
import Ubuntu.Components 1.2


Page {
    id: appAddView
    title: i18n.tr("Install Apps")
    property var search_comp: null
    property var search_obj: null
    property var install_signal: null

    Label {
        id: searchPackageMessage

        visible: false

        Layout.fillWidth: true
        wrapMode: Text.Wrap
        horizontalAlignment: Text.AlignHCenter

        text: i18n.tr("Please enter a package name to search for:")
    }

    TextField {
        id: searchString

        visible: false

        anchors {
            top: searchPackageMessage.bottom
            horizontalCenter: parent.horizontalCenter
            margins: units.gu(1)
        }
        height: units.gu(4.5)
        width: parent.width - anchors.margins * 2

        onAccepted: {
            if (searchInstallMessage.visible) {
                searchInstallMessage.visible = false
                searchInstallMessage.text = ""
            }
            searchPackage(searchString.text)
        }
    }

    Label {
        id: enterPackageMessage

        visible: false

        Layout.fillWidth: true
        wrapMode: Text.Wrap
        horizontalAlignment: Text.AlignHCenter

        text: i18n.tr("Please enter the exact package name or path to a Debian package to install:")
    }

    TextField {
        id: appName

        visible: false

        anchors {
            top: enterPackageMessage.bottom
            horizontalCenter: parent.horizontalCenter
            margins: units.gu(1)
        }
        height: units.gu(4.5)
        width: parent.width - anchors.margins * 2

        onAccepted: {
            var package_name = text
            if (containerConfigList.isValidDebianPackage(text)) {
                package_name = containerConfigList.getDebianPackageName(text)
            }
            if (!containerConfigList.isAppInstalled(mainView.currentContainer, package_name)) {
                installPackage(text)
                containerAppsList.setContainerApps(mainView.currentContainer)
                mainView.currentPackage = package_name
                pageStack.pop()
                pageStack.push(Qt.resolvedUrl("PackageInfoView.qml"), {install_signal: install_signal})
            }
            else {
                appInstallMessage.text = i18n.tr("Package %1 already installed. Please try a different package name.").arg(text)
                appInstallMessage.visible = true
                appName.text = ""
            }  
        }
    }

    Label {
        id: appInstallMessage

        visible: false

        anchors {
            top: appName.bottom
            margins: units.gu(3)
        }
        height: units.gu(4.5)
    }

    Label {
        id: searchInstallMessage

        visible: false

        anchors {
            top: searchString.bottom
            margins: units.gu(3)
        }
        height: units.gu(4.5)
    }

    head.actions: [
        Action {
            iconName: "search"
            text: i18n.tr("Search for package")
            description: i18n.tr("Search for packages in archives based on the search string entered.")
            onTriggered: {
                if (search_obj) {
                    search_obj.destroy()
                    packageListModel.clear()
                }
                if (enterPackageMessage.visible) {
                    enterPackageMessage.visible = false
                    appName.visible = false
                    appName.text = ""
                    appInstallMessage.visible = false
                    appInstallMessage.text = ""
                }
                if (searchInstallMessage.visible) {
                    searchInstallMessage.visible = false
                    searchInstallMessage.text = ""
                }
                searchPackageMessage.visible = true
                searchString.visible = true
                searchString.forceActiveFocus()
            }
        },
        Action {
            iconName: "settings"
            text: i18n.tr("Enter package name")
            description: i18n.tr("Enter the exact package name to install.")
            onTriggered: {
                if (search_obj) {
                    search_obj.destroy()
                    packageListModel.clear()
                }
                if (searchPackageMessage.visible) {
                    searchPackageMessage.visible = false
                    searchString.visible = false
                    searchString.text = ""
                    searchInstallMessage.visible = false
                    searchInstallMessage.text = ""
                }
                enterPackageMessage.visible = true
                appName.visible = true
                appName.forceActiveFocus()
            }
        }
    ]

    ListModel {
        id: packageListModel
    }

    function installPackage(package_name) {
        var comp = Qt.createComponent("ContainerManager.qml")
        var worker = comp.createObject(mainView, {"containerAction": ContainerManagerWorker.Install,
                                                  "containerId": mainView.currentContainer,
                                                  "containerType": containerConfigList.getContainerType(mainView.currentContainer),
                                                  "data": package_name})
        install_signal = worker.finishedInstall
        worker.start()
    }

    function searchPackage(search_string) {
        var comp = Qt.createComponent("ContainerManager.qml")
        var worker = comp.createObject()
        worker.containerAction = ContainerManagerWorker.Search
        worker.containerId = mainView.currentContainer
        worker.data = search_string
        worker.finishedSearch.connect(finishedSearch)
        worker.start()
    }

    function finishedSearch(result, packageList) {
        if (result) {
            for (var i = 0; i < packageList.length; ++i)
            {
                packageListModel.append({"package_desc": packageList[i], "package_name": packageList[i].split(' ')[0]})
            }
            searchPackageMessage.visible = false
            searchString.visible = false
            searchString.text = ""
            if (!search_comp) {
                search_comp = Qt.createComponent("SearchResults.qml")
            }
            search_obj = search_comp.createObject(appAddView, {"model": packageListModel})
        }
        else {
            searchInstallMessage.text = i18n.tr("No search results for %1.").arg(searchString.text)
            searchInstallMessage.visible = true
        }
            
    }
}
