/*
 * Copyright 2015 Canonical Ltd.
 *
 * This program is free software: you can redistribute it and/or modify it under
 * the terms of the GNU General Public License, version 3, as published by the
 * Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <glib.h>

#ifndef _LIBERTINE_COMMON_H_
#define _LIBERTINE_COMMON_H_

#ifdef __cplusplus
extern "C" {
#endif

/**
 * libertine_list_containers:
 * 
 * Gets the list of existing containers for the user.
 *
 * Return value: (transfer full): A NULL terminated list of
 *     container IDs.  Should be free'd with g_strfreev().
 */
gchar ** libertine_list_containers(void);

/**
 * libertine_container_path:
 * @container_id: ID of the container
 *
 * Calculates the full path to the rootfs of @container_id.
 *
 * Return value: Path to the rootfs or NULL if it is not found.
 *     Should be free'd with g_free().
 */
gchar * libertine_container_path(const gchar * container_id);

/**
 * libertine_container_home_path:
 * @container_id: ID of the container
 *
 * Calculates the path to the mapped home dir of @container_id.
 *
 * Return value: Path to the mapped home dir or NULL if it is not found.
 *     Should be free'd with g_free().
 */
gchar * libertine_container_home_path(const gchar * container_id);

/**
 * libertine_container_name:
 * @container_id: ID of the container
 *
 * Gets the human readable name of @container_id.
 *
 * Return value: Human readable string for @container_id.
 *     Should be free'd with g_free().
 */
gchar * libertine_container_name(const gchar * container_id);

/**
 * libertine_list_apps_for_container:
 * @container_id: ID of the container
 * 
 * Gets the list of existing apps installed in a container.
 *
 * Return value: (transfer full): A NULL terminated list of
 *     app IDs.  Should be free'd with g_strfreev().
 */
gchar ** libertine_list_apps_for_container(const gchar * container_id);

#ifdef __cplusplus
}
#endif

#endif /* _LIBERTINE_COMMON_H_ */
