/**
 * @file AddExtraArchiveView.qml
 * @brief Libertine container add archive view
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
import Ubuntu.Components 1.3

Page {
    id: addExtraArchiveView
    header: PageHeader {
        id: pageHeader
        title: i18n.tr("Add Archive")
    }
    property string currentContainer: ""

    signal error(string short_description, string details)

    Column {
        spacing: units.gu(2)

        anchors {
            topMargin: pageHeader.height + units.gu(2)
            leftMargin: units.gu(2)
            rightMargin: units.gu(2)
            fill: parent
        }

        Label {
            text: i18n.tr("New archive identifier, e.g.")
            anchors {
                left: parent.left
                right: parent.right
            }
        }

        TextEdit {
            text: i18n.tr("multiverse\nppa:user/repository\ndeb http://myserver/repo stable repo")
            anchors {
                left: parent.left
                right: parent.right
                leftMargin: units.gu(4)
            }

            readOnly: true
            color: theme.palette.normal.backgroundSecondaryText
        }

        TextField {
            id: extraArchiveString
            anchors {
                left: parent.left
                right: parent.right
            }
            onAccepted: {
                addArchive()
            }
        }

        Label {
            text: i18n.tr("(Optional) Public signing key for archive")
            anchors {
                left: parent.left
                right: parent.right
            }
        }

        TextArea {
            id: publicSigningKey
            anchors {
                left: parent.left
                right: parent.right
            }
            height: Math.max(addExtraArchiveView.height/3, units.gu(6))
        }

        Button {
            text: i18n.tr("Add")
            color: theme.palette.normal.positive
            onClicked: {
                addArchive()
            }
        }
    }

    function addArchive() {
        var worker = Qt.createComponent("ContainerManager.qml").createObject(parent)
        worker.finishedConfigure.connect(finishedConfigure)
        worker.error.connect(addExtraArchiveView.error)
        worker.addArchive(currentContainer, containerConfigList.getContainerName(currentContainer),
                          extraArchiveString.text, publicSigningKey.text.trim())

        pageStack.removePages(addExtraArchiveView)
    }

    Component.onCompleted: {
        extraArchiveString.forceActiveFocus()
    }

    function finishedConfigure() {
        if (addExtraArchiveView) {
            containerArchivesList.setContainerArchives(currentContainer)
        }
    }
}
