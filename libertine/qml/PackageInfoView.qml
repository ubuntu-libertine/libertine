/**
 * @file PackageInfoView.qml
 * @brief Container package info view
 */
/*
 * Copyright 2016 Canonical Ltd
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
import QtQuick.Layouts 1.0
import Ubuntu.Components 1.2


Page {
    id: packageInfoView
    title: i18n.tr("Information for the ") + mainView.currentPackage + i18n.tr(" package")
    property string currentContainer: mainView.currentContainer
    property var currentPackage: mainView.currentPackage
    property var statusText: containerConfigList.getAppStatus(currentContainer, currentPackage)

    Label {
        id: packageStatus
        text: i18n.tr("Install status: ") + statusText
        fontSize: "large"
    }

    Component.onCompleted: {
        containerConfigList.configChanged.connect(reloadStatus)
    }

    Component.onDestruction: {
        containerConfigList.configChanged.disconnect(reloadStatus)
    }

    function reloadStatus() {
        statusText = containerConfigList.getAppStatus(currentContainer, currentPackage) 

        if (!statusText) {
            statusText = "removed"
        }
    }
}
