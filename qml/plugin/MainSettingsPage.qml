/*
 * Copyright (C) 2016-2017 Canonical Ltd.
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License version 3, as published
 * by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranties of
 * MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
 * PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.4
import Ubuntu.Components 1.3
import Ubuntu.Components.Popups 1.3
import SystemSettings 1.0
import Libertine 1.0
import "../common"

ItemPage {
    id: containersView
    clip: true

    header: PageHeader {
        id: pageHeader
        title: i18n.tr("Manage Libertine Containers")
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
    property var operationDetails

    signal error(string short_description, string details)

    ContainersList {
        anchors {
            topMargin: pageHeader.height
            fill: containersView
        }

        currentContainer: containersView.currentContainer
    }

    onError: {
        PopupUtils.open(Qt.resolvedUrl("../common/GenericErrorDialog.qml"), null,
                                       {"short_description": short_description, "details": details})
    }
}
