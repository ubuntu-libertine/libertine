/**
 * @file ContainersView.qml
 * @brief Libertine containers view
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
import "../common"


/**
 * View providing a list of available containers and their (possibly animated)
 * states.
 */
Page {
    id: containersView
    header: PageHeader {
        id: pageHeader
        title: i18n.tr("My Containers")
        trailingActionBar.actions: [
            Action {
                iconName: "add"
                onTriggered: {
                    PopupUtils.open(Qt.resolvedUrl("../common/ContainerOptionsDialog.qml"))
                }
            }
        ]
    }
    property string currentContainer

    ContainersList {
        anchors {
            topMargin: pageHeader.height
            fill: containersView
        }

        currentContainer: containersView.currentContainer
    }
}
