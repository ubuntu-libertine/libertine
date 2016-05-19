/**
 * @file libertine.qml
 * @brief Libertine app main view.
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

import QtQuick 2.4
import Ubuntu.Components 1.3
import Ubuntu.Components.Popups 1.3


MainView {
    id: mainView
    objectName: "mainView"
    applicationName: "libertine"
    width:  units.gu(90)
    height: units.gu(75)
    property var currentContainer: undefined
    property var packageOperationDetails: undefined

    signal error(string short_description, string details)
    signal updatePackageDetails(string container_id, string package_name, string details)
    signal packageOperationInteraction(string data)

    PageStack {
        id: pageStack
    }

    Component.onCompleted: {
        mainView.currentContainer = containerConfigList.defaultContainerId

        if (!containerConfigList.empty()) {
            pageStack.push(Qt.resolvedUrl("ContainersView.qml"))
            if (mainView.currentContainer) {
                containerAppsList.setContainerApps(mainView.currentContainer)
                pageStack.push(Qt.resolvedUrl("HomeView.qml"), {"currentContainer": mainView.currentContainer})
            }
        }
        else {
            pageStack.push(Qt.resolvedUrl("WelcomeView.qml"))
        }
    }

    onError: {
        PopupUtils.open(Qt.resolvedUrl("GenericErrorDialog.qml"), null,
                                       {"short_description": short_description, "details": details})
    }

    function updatePackageOperationDetails(container_id, package_name, details) {
        if (!packageOperationDetails) {
            packageOperationDetails = {}
        }
        if (!packageOperationDetails[container_id]) {
            packageOperationDetails[container_id] = {}
        }
        if (!packageOperationDetails[container_id][package_name]) {
            packageOperationDetails[container_id][package_name] = ""
        }
        packageOperationDetails[container_id][package_name] += details

        updatePackageDetails(container_id, package_name, details)
    }

    function resetPackageDetails(container_id, package_name) {
        if (packageOperationDetails && packageOperationDetails[container_id] && packageOperationDetails[container_id][package_name]) {
            delete packageOperationDetails[container_id][package_name]
        }
    }

    function getPackageOperationDetails(container_id, package_name) {
        if (packageOperationDetails && packageOperationDetails[container_id] && packageOperationDetails[container_id][package_name]) {
            return packageOperationDetails[container_id][package_name]
        }
        return ""
    }
}
