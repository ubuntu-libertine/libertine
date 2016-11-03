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

    signal error(string short_description, string details)

    PageStack {
        id: pageStack
    }

    Component.onCompleted: {
        packageOperationDetails.error.connect(error)

        Qt.createComponent("../common/ContainerManager.qml").createObject(mainView).fixIntegrity()

        var currentContainer = containerConfigList.defaultContainerId

        if (!containerConfigList.empty()) {
            pageStack.push(Qt.resolvedUrl("ContainersView.qml"), {currentContainer: currentContainer})
            if (currentContainer) {
                containerAppsList.setContainerApps(currentContainer)
                pageStack.push(Qt.resolvedUrl("../common/ContainerEditView.qml"), {currentContainer: currentContainer})
            }
        }
        else {
            pageStack.push(Qt.resolvedUrl("WelcomeView.qml"))
        }
    }

    onError: {
        PopupUtils.open(Qt.resolvedUrl("../common/GenericErrorDialog.qml"), null,
                                       {"short_description": short_description, "details": details})
    }
}
