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
#include "libertine/ContainerConfigList.h"
#include "libertine/LibertineConfig.h"


gchar **
libertine_list_containers(void)
{
  guint container_count,
        i;
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
  gchar * path = NULL;
  g_return_val_if_fail(container_id != NULL, NULL);

  path = g_build_filename(g_get_user_cache_dir(), "libertine-container", container_id, "rootfs", NULL);

  if (g_file_test(path, G_FILE_TEST_EXISTS))
  {
    return path;
  }
  else
  {
    g_free(path);
    return NULL;
  }
}


gchar *
libertine_container_home_path(const gchar * container_id)
{
  gchar * path = NULL;
  g_return_val_if_fail(container_id != NULL, NULL);

  path = g_build_filename(g_get_user_data_dir(), "libertine-container", "user-data", container_id, NULL);

  if (g_file_test(path, G_FILE_TEST_EXISTS))
  {
    return path;
  }
  else
  {
    g_free(path);
    return NULL;
  }

}


gchar *
libertine_container_name(const gchar * container_id)
{
  guint container_count,
        i;
  gchar * container_name = NULL;
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
