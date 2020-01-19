/**
 * @file SearchPackagesDialog.qml
 * @brief Libertine search packages dialog
 */
/*
 * Copyright 2016-2017 Canonical Ltd
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


Dialog {
    id: searchPackageDialog
    title: i18n.tr("Search a package")
    text: i18n.tr("Search a package in the archives by name")
    property bool calledFromSearch: null
    property string currentContainer: null

    signal initializeSearch(string query, string container)

    TextField {
        id: searchPackageInput
        placeholderText: i18n.tr("Search")
        //Fixes issue #50. Ok button doesn't search
        inputMethodHints: Qt.ImhNoPredictiveText
        onAccepted: okButton.clicked()
    }

    Row {
        spacing: units.gu(1)

        Button {
            id: cancelButton
            text: i18n.tr("Cancel")
            width: (parent.width - parent.spacing) / 2
            onClicked: {
                PopupUtils.close(searchPackageDialog)
            }
        }

        Button {
            id: okButton
            text: i18n.tr("Search")
            color: theme.palette.normal.positive
            width: (parent.width - parent.spacing) / 2
            onClicked: {
                if (searchPackageInput.text != "") {
                    PopupUtils.close(searchPackageDialog)
                    initializeSearch(searchPackageInput.text, currentContainer)
                }
            }
        }
    }

    Component.onCompleted: searchPackageInput.forceActiveFocus()
}
