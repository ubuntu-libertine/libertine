/**
 * @file PackageOperationFailureDialog.qml
 * @brief Libertine package operation failure dialog
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
    id: genericErrorDialog
    property string short_description: ""
    property string details: ""

    title: short_description

    TextEdit {
        color: theme.palette.normal.backgroundSecondaryText
        text: details
        readOnly: true
        selectByMouse: true
        wrapMode: TextEdit.WordWrap
    }

    Button {
        text: i18n.tr("Dismiss")
        color: theme.palette.normal.focus
        onClicked: PopupUtils.close(genericErrorDialog)
    }

    Button {
        text: i18n.tr("Copy to Clipboard")
        onClicked: {
            Clipboard.push(details)
        }
    }
}
