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
import Ubuntu.Components 0.1

MainView {
    id: mainView
    objectName: "mainView"
    applicationName: "Legacy Application Manager"
    useDeprecatedToolbar: false
    width: units.gu(60)
    height: units.gu(75)
    property real margins: units.gu(2)

    PageStack {
        id: pageStack
        state: "WELCOME"
        property string pageName: "welcomeview.qml"  // initial state

        Component.onCompleted: {
            push(Qt.resolvedUrl(pageName))
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
            PropertyChanges { target: pageStack; pageName: "welcomeview.qml"}
        },
        State {
            name: "INSTALL_PROGRESS"
            PropertyChanges { target: pageStack; pageName: "installprogressview.qml"}
        }
    ]
}
