/**
 * @file libertine.qml
 * @brief Libertine app main view.
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
import QtQuick 2.4
import Ubuntu.Components 1.2


MainView {
    id: mainView
    objectName: "mainView"
    applicationName: "libertine"
    width:  units.gu(90)
    height: units.gu(75)
    property var currentContainer: undefined

    PageStack {
        id: pageStack
    }

    Component.onCompleted: {
        mainView.currentContainer = containerConfigList.defaultContainerId

        if (mainView.currentContainer) {
            containerAppsList.setContainerApps(mainView.currentContainer)
            pageStack.push(Qt.resolvedUrl("HomeView.qml"))
        }
        else if (!containerConfigList.empty()) {
            pageStack.push(Qt.resolvedUrl("ContainersView.qml"))
        }
        else {
            pageStack.push(Qt.resolvedUrl("WelcomeView.qml"))
        }
    }
}
