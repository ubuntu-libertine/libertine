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
    property var currentPackage: undefined

    signal packageInstallFinished(string package_name, bool result, string message)
    signal packageRemoveFinished(string package_name, bool result, string message)

    PageStack {
        id: pageStack
    }

    Component.onCompleted: {
        mainView.currentContainer = containerConfigList.defaultContainerId

        if (!containerConfigList.empty()) {
            pageStack.push(Qt.resolvedUrl("ContainersView.qml"))
            if (mainView.currentContainer) {
                containerAppsList.setContainerApps(mainView.currentContainer)
                pageStack.push(Qt.resolvedUrl("HomeView.qml"))
            }
        }
        else {
            pageStack.push(Qt.resolvedUrl("WelcomeView.qml"))
        }
    }

    onPackageInstallFinished: {
        if (!result) {
           PopupUtils.open(Qt.resolvedUrl("PackageOperationFailureDialog.qml"), null,
                                          {"package_name": package_name, "error_msg": message, "operation": i18n.tr("installing")})
        }
    }

    onPackageRemoveFinished: {
        if (!result) {
           PopupUtils.open(Qt.resolvedUrl("PackageOperationFailureDialog.qml"), null,
                           {"package_name": package_name, "error_msg": message, "operation": i18n.tr("removing")})
        }
    }
}
