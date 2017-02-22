/*
 * Copyright 2017 Canonical Ltd
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
import QtQuick.Dialogs 1.0

FileDialog {
    id: addBindMountDialog
    title: "Choose directory to bind-mount"
    selectFolder: true
    onAccepted: {
        if (addBindMountDialog.fileUrl) {
            extraBindMountsView.addBindMount(addBindMountDialog.fileUrl.toString().replace("file:///", "/"))
        }
    }
}
