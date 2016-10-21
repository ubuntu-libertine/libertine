/**
 * @file libertine_common.cpp
 * @brief The Libertine Common shared library
 */
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
#include "liblibertine/libertine.h"

#include "common/ContainerConfigList.h"
#include "common/LibertineConfig.h"


namespace
{
constexpr auto DESKTOP_EXTENSION   = ".desktop";
constexpr auto GLOBAL_APPLICATIONS = "usr/share/applications";
constexpr auto LOCAL_APPLICATIONS  = ".local/share/applications";


GError*
list_apps_from_path(gchar* path, const gchar* container_id, GArray* apps)
{
  GError* error = nullptr;
  GDir* dir = g_dir_open(path, 0, &error);
  if (error != nullptr)
  {
    return error;
  }

  const gchar * files;
  while ((files = g_dir_read_name(dir)) != nullptr)
  {
    gchar *file = g_build_filename(path, files, nullptr);
    if (g_file_test(file, G_FILE_TEST_IS_REGULAR) && g_str_has_suffix(files, DESKTOP_EXTENSION))
    {
      auto name = g_strdup(files);
      name[strlen(name)-strlen(DESKTOP_EXTENSION)] = 0; // truncate the file extension

      gchar * app_id = g_strjoin("_", g_strdup(container_id), name, "0.0", nullptr);
      g_array_append_val(apps, app_id);
      g_free(name);
    }
    else if (g_file_test(file, G_FILE_TEST_IS_DIR))
    {
      error = list_apps_from_path(file, container_id, apps);
      if (error != nullptr)
      {
        return error;
      }
    }
    g_free(file);
  }

  g_dir_close(dir);
  return nullptr;
}
}


gchar**
libertine_list_apps_for_container(const gchar* container_id)
{
  g_return_val_if_fail(container_id != nullptr, nullptr);
  gchar* path = libertine_container_path(container_id);
  GError* error = nullptr;
  GArray* apps = g_array_new(TRUE, TRUE, sizeof(gchar*));

  if (path != nullptr)
  {
      auto global_path = g_build_filename("/", g_strdup(path), GLOBAL_APPLICATIONS, nullptr);
      error = list_apps_from_path(global_path, container_id, apps);
      if (error != nullptr)
      {
        g_free(global_path);
        g_free(path);
        g_error_free(error);
        return (gchar**)g_array_free(apps, FALSE);
      }
      g_free(global_path);
  }
  g_free(path);

  auto home_path = libertine_container_home_path(container_id);
  if (home_path != nullptr)
  {
      auto local_path = g_build_filename(home_path, LOCAL_APPLICATIONS, nullptr);

      error = list_apps_from_path(local_path, container_id, apps);
      if (error != nullptr)
      {
        g_error_free(error); // free error, but return previously found apps
      }
      g_free(local_path);
  }
  g_free(home_path);

  return (gchar**)g_array_free(apps, FALSE);
}


gchar **
libertine_list_containers(void)
{
  guint container_count;
  guint i;
  LibertineConfig config;
  ContainerConfigList container_list(&config);
  GArray * containers = g_array_new(TRUE, TRUE, sizeof(gchar *));
  QVariant id;

  container_count = (guint)container_list.size();

  for (i = 0; i < container_count; ++i)
  {
    id = container_list.data(container_list.index(i, 0), (int)ContainerConfigList::DataRole::ContainerId);
    gchar * container_id = g_strdup((gchar *)id.toString().toStdString().c_str());
    g_array_append_val(containers, container_id);
  }

  return (gchar **)g_array_free(containers, FALSE);
}


gchar *
libertine_container_path(const gchar * container_id)
{
  gchar * path = nullptr;
  g_return_val_if_fail(container_id != nullptr, nullptr);

  path = g_build_filename(g_get_user_cache_dir(), "libertine-container", container_id, "rootfs", nullptr);

  if (g_file_test(path, G_FILE_TEST_EXISTS))
  {
    return path;
  }
  else
  {
    g_free(path);
    return nullptr;
  }
}


gchar *
libertine_container_home_path(const gchar * container_id)
{
  gchar * path = nullptr;
  g_return_val_if_fail(container_id != nullptr, nullptr);

  path = g_build_filename(g_get_user_data_dir(), "libertine-container", "user-data", container_id, nullptr);

  if (g_file_test(path, G_FILE_TEST_EXISTS))
  {
    return path;
  }
  else
  {
    g_free(path);
    return nullptr;
  }

}


gchar *
libertine_container_name(const gchar * container_id)
{
  guint container_count;
  guint i;
  gchar * container_name = nullptr;
  LibertineConfig config;
  ContainerConfigList container_list(&config);
  QVariant id;

  container_count = (guint)container_list.size();

  for (i = 0; i < container_count; ++i)
  {
    id = container_list.data(container_list.index(i, 0), (int)ContainerConfigList::DataRole::ContainerId);

    if (g_strcmp0((gchar *)id.toString().toStdString().c_str(), container_id) == 0)
    {
      QVariant name = container_list.data(container_list.index(i, 0), (int)ContainerConfigList::DataRole::ContainerName);
      container_name = g_strdup(name.toString().toStdString().c_str());
      break;
    }
  }

  return container_name;
}
