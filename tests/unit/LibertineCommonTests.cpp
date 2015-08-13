/**
 * @file tests/unit/LibertineCommonTests.cpp
 * @brief Verify the Libertine Common shared library
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
#include <gtest/gtest.h>

#include "libertine/libertine_common.h"

TEST(LibertineCommon, ListContainers)
{
  g_setenv("XDG_DATA_HOME", CMAKE_SOURCE_DIR "/libertine-config/libertine", TRUE);

  gchar ** containers = libertine_list_containers();

  ASSERT_NE(containers, nullptr);
  ASSERT_EQ(g_strv_length(containers), 2);

  ASSERT_STREQ("wily", containers[0]);
  ASSERT_STREQ("wily-2", containers[1]);

  g_strfreev(containers);
}

TEST(LibertineCommon, ContainerPath)
{
  g_setenv("XDG_CACHE_HOME", CMAKE_SOURCE_DIR "/libertine-data", TRUE);

  gchar * container_id = g_strdup("wily");

  gchar * container_path = libertine_container_path(container_id);

  EXPECT_STREQ(CMAKE_SOURCE_DIR "/libertine-data/libertine-container/wily/rootfs", container_path);

  g_free(container_id);
  g_free(container_path);
}

TEST(LibertineCommon, ContainerHomePath)
{
  g_setenv("XDG_DATA_HOME", CMAKE_SOURCE_DIR "/libertine-home", TRUE);

  gchar * container_id = g_strdup("wily");

  gchar * container_home_path = libertine_container_home_path(container_id);

  EXPECT_STREQ(CMAKE_SOURCE_DIR "/libertine-home/libertine-container/user-data/wily", container_home_path);

  g_free(container_id);
  g_free(container_home_path);
}

TEST(LibertineCommon, ContainerName)
{
  g_setenv("XDG_DATA_HOME", CMAKE_SOURCE_DIR "/libertine-config/libertine", TRUE);

  gchar * container_id = g_strdup("wily");
  gchar * container_name = libertine_container_name(container_id);

  ASSERT_STREQ("Ubuntu 'Wily Werewolf'", container_name);

  g_free(container_id);
  g_free(container_name);

  container_id = g_strdup("wily-2");
  container_name = libertine_container_name(container_id);

  ASSERT_STREQ("Ubuntu 'Wily Werewolf' (2)", container_name);

  g_free(container_id);
  g_free(container_name);
}
