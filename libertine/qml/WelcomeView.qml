/**
 * @file WelcomeView.qml
 * @brief Libertine default welcome view
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
import QtQuick.Layouts 1.0
import Ubuntu.Components 0.1


Page {
    id: welcomeView
    title: "Welcome"

    ColumnLayout {
        spacing: units.gu(2)
        anchors {
           fill: parent
           margins: units.gu(4)
        }

        Label {
            id: welcome_message
            anchors {
                left: parent.left
                right: parent.right
            }
            wrapMode: Text.Wrap
            horizontalAlignment: Text.AlignHCenter

            text: "Welcome to the Ubuntu Legacy Application Support Manager."
        }
        Label {
            id: warning_message
            anchors {
                left: parent.left
                right: parent.right
            }
            wrapMode: Text.Wrap
            horizontalAlignment: Text.AlignHCenter

            text: "You do not have Legacy Application Support configured at" +
                  " this time.  Downloading and setting up the required" +
                  " environment takes some time and network bandwidth."
        }
        Button {
            id: install_button
            anchors{
                left: parent.left
                right: parent.right
                margins: units.gu(4)
            }

            text: i18n.tr("Install")
            color: UbuntuColors.lightAubergine
            onClicked: {
                mainView.state = "PREPARE_CONTAINER"
            }

        }
    }
}
