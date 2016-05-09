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
    id: packageOperationFailedDialog
    property var package_name: null
    property var error_msg: null
    property var operation: null // Either "installing" or "removing"

    title: i18n.tr("Failure %1 the %2 package.").arg(operation).arg(package_name)
    text: error_msg

    Button {
        text: i18n.tr("Dismiss")
        onClicked: PopupUtils.close(packageOperationFailedDialog)
    }
}
