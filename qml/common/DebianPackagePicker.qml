/**
 * @file DebianPackagePicker.qml
 * @brief Libertine container Debian package picker view
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

import QtQuick 2.4
import Ubuntu.Components 1.3


Page {
    id: debianPackagePicker
    header: PageHeader {
        id: pageHeader
        title: i18n.tr("Available Debian Packages to Install")
    }

    signal packageSelected(string packageName)
    property var packageList: null

    ListModel {
        id: packageListModel
    }

    UbuntuListView {
        id: listView
        anchors {
            topMargin: pageHeader.height
            fill: parent
        }
        model: packageListModel
        visible: packageList.length > 0  ? true : false

        function install(fileName) {
            pageStack.removePages(debianPackagePicker)
            debianPackagePicker.packageSelected(containerConfigList.getDownloadsLocation() + "/" + fileName)
        }

        delegate: ListItem {
            id: packageItem
            Label {
                text: model.file_name
                anchors {
                    verticalCenter: parent.verticalCenter
                    left: parent.left
                    leftMargin: units.gu(2)
                }
            }

            onClicked: {
                listView.install(model.file_name)
            }

            trailingActions: ListItemActions {
                actions: [
                    Action {
                        iconName: "select"
                        description: i18n.tr("Install Package")
                        onTriggered: {
                            listView.install(model.file_name)
                        }
                    }
                ]
            }
        }
    }

    Label {
        id: emptyLabel
        anchors.centerIn: parent
        visible: packageList.length == 0  ? true : false
        wrapMode: Text.Wrap
        width: parent.width
        horizontalAlignment: Text.AlignHCenter
        text: i18n.tr("No Debian packages available")
    }

    Component.onCompleted: {
        for (var i = 0; i < packageList.length; ++i)
        {
            packageListModel.append({"file_name":  packageList[i]})
        }
    }
}
