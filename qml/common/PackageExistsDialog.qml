/**
 * @file PackageExistsDialog.qml
 * @brief Libertine search packages dialog
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
import Ubuntu.Components.Popups 1.3


Dialog {
    id: packageExistsDialog
    property var package_name: null
    property var search_again: false
    title: i18n.tr("The %1 package is already installed.").arg(package_name)
    text: i18n.tr("Search again or return to search results.")

    Button {
        id: searchAgain
        text: i18n.tr("Search again")
        color: theme.palette.normal.positive
        onClicked: {
            search_again = true
            PopupUtils.close(packageExistsDialog)
        }
    }

    Button {
        id: returnToResults
        text: i18n.tr("Return to search results")
        onClicked: {
            PopupUtils.close(packageExistsDialog)
        }
    }

    Component.onDestruction: {
        if (search_again) {
            pageStack.currentPage.doSearch()
        }
    }
}
