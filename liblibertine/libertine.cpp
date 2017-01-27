/**
 * @file libertine.cpp
 * @brief The Libertine Common shared library
 */
/*
 * Copyright 2015-2017 Canonical Ltd.
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

#include "liblibertine/libertine.h"
#include "liblibertine/libertined.h"


gchar**
libertine_list_apps_for_container(const gchar* container_id)
{
  g_return_val_if_fail(container_id != nullptr, nullptr);
  GArray* apps = g_array_new(TRUE, TRUE, sizeof(gchar*));
  for (auto const& app: libertined_list_app_ids(container_id))
  {
    auto app_id = g_strdup((gchar *)app.toString().toStdString().c_str());
    g_array_append_val(apps, app_id);
  }

  return (gchar**)g_array_free(apps, FALSE);
}


gchar **
libertine_list_containers(void)
{
  auto containers = g_array_new(TRUE, TRUE, sizeof(gchar *));
  for (auto const& container: libertined_list())
  {
    auto container_id = g_strdup((gchar *)container.toString().toStdString().c_str());
    g_array_append_val(containers, container_id);
  }
  return (gchar **)g_array_free(containers, FALSE);
}


gchar *
libertine_container_path(const gchar * container_id)
{
  g_return_val_if_fail(container_id != nullptr, nullptr);

  gchar* path = g_strdup((gchar *)libertined_container_path(container_id).toStdString().c_str());
  if (g_file_test(path, G_FILE_TEST_EXISTS))
  {
    return path;
  }

  g_free(path);
  return nullptr;
}


gchar *
libertine_container_home_path(const gchar * container_id)
{
  g_return_val_if_fail(container_id != nullptr, nullptr);

  gchar* path = g_strdup((gchar *)libertined_container_home_path(container_id).toStdString().c_str());
  if (g_file_test(path, G_FILE_TEST_EXISTS))
  {
    return path;
  }

  g_free(path);
  return nullptr;
}


gchar *
libertine_container_name(const gchar * container_id)
{
  g_return_val_if_fail(container_id != nullptr, nullptr);

  return g_strdup((gchar *)libertined_container_name(container_id).toStdString().c_str());
}
