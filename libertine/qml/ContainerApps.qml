/**
 * @file ContainerApps.qml
 * @brief Libertine container apps data source
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
import QtQuick 2.4
import U1db 1.0 as U1db

Item {

    U1db.Document {
        id: containerApps
        database: configDB
        docId: "ContainerApps"
    }

    U1db.Index {
        database: configDB
	id: containerAppIndex
	name: "containerAppIndex"
	expression: [ "containerId", "appId" ]
    }

    U1db.Query {
        id: appsForContainer
	index: containerAppIndex
	query: [{"containerId":mainView.containerId},{"appId":"*"}]
    }

    function are_apps_installed(containerId) {
        var documentIds = {}

        documentIds = configDB.listDocs()
        return documentIds.length > 0
    }
}
