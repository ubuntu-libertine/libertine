/**
 * @file libertine.qml
 * @brief Libertine app main view.
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

    Component.onCompleted: {
        containerOperationDetails.error.connect(error)
        Qt.createComponent("../common/ContainerManager.qml").createObject(mainView).fixIntegrity()
    }

    onError: {
        PopupUtils.open(Qt.resolvedUrl("../common/GenericErrorDialog.qml"), null,
                                       {"short_description": short_description, "details": details})
    }

    AdaptivePageLayout {
        anchors.fill: parent
        primaryPageSource: Qt.resolvedUrl("ContainersView.qml")
        layouts: [
            PageColumnsLayout {
                when: width > units.gu(120)
                PageColumn {
                    minimumWidth: units.gu(30)
                    maximumWidth: units.gu(60)
                    preferredWidth: units.gu(40)
                }
                PageColumn {
                    minimumWidth: units.gu(30)
                    maximumWidth: units.gu(60)
                    preferredWidth: units.gu(40)
                }
                PageColumn {
                    fillWidth: true
                }
            },
            PageColumnsLayout {
                when: width > units.gu(80)
                PageColumn {
                    minimumWidth: units.gu(30)
                    maximumWidth: units.gu(60)
                    preferredWidth: units.gu(40)
                }
                PageColumn {
                    fillWidth: true
                }
            }
        ]
    }
}
