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

#pragma once

#include <QDBusConnection>
#include <QJsonArray>

QJsonArray libertined_list();
QString    libertined_container_path(char const* container_id);
QString    libertined_container_home_path(char const* container_id);
QString    libertined_container_name(char const* container_id);
QJsonArray libertined_list_app_ids(char const* container_id);
