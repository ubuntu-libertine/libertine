/**
 * @file tests/unit/ContainerConfigTests.cpp
 * @brief Verify the COntainerConfig class
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

#include "libertine/ContainerConfig.h"

/** Verify constructing a New containerConfig DTRT. */
TEST(LibertineContainerConfig, constructFromScalars)
{
  ContainerConfig container_config("id", "name", "image");

  ASSERT_EQ(container_config.container_id(),   "id");
  ASSERT_EQ(container_config.name(),           "name");
  ASSERT_EQ(container_config.image_id(),       "image");
  ASSERT_EQ(container_config.install_status(), ContainerConfig::InstallStatus::New);
}
