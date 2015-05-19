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
import QtQuick 2.0
import Ubuntu.Components 1.1


MainView {
    id: mainView
    objectName: "mainView"
    applicationName: "libertine"
    useDeprecatedToolbar: false
    width:  units.gu(48)
    height: units.gu(75)
    property string currentContainerId: ""

    ContainerConfig {
        id: containerConfig
    }

    PageStack {
        id: pageStack
        state: "WELCOME"
        property string pageName: "WelcomeView.qml"  // default initial state

        Component.onCompleted: {
            push(Qt.resolvedUrl(pageName))
            if (containerConfig.are_containers_available())
            {
                mainView.currentContainerId = "demo"
                pageName = "HomeView.qml"
            }
        }

        onPageNameChanged: {
            pop();
            push(Qt.resolvedUrl(pageName))
        }
    }

    // The pages/views will set the state to the next one when it is done
    // like this: onClicked: {mainView.state = "TESTSELECTION"}
    states: [
        State {
            name: "WELCOME"
            PropertyChanges {
                target:   pageStack
                pageName: "WelcomeView.qml"
            }
        },
        State {
            name: "PREPARE_CONTAINER"
            PropertyChanges {
                target:   pageStack
                pageName: "PreparingContainerView.qml"
            }
        },
        State {
            name: "HOMEPAGE"
            PropertyChanges {
                target:   pageStack
                pageName: "HomeView.qml"
            }
        },
        State {
            name: "ADD_APPS"
            PropertyChanges {
                target:   pageStack
                pageName: "AppAddView.qml"
            }
        }
    ]
}
