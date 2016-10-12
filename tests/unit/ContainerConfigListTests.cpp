/**
 * @file tests/unit/ContainerConfigLIstTests.cpp
 * @brief Verify the ContainerConfig class
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

#include "common/ContainerConfigList.h"
#include <QtCore/QByteArray>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonParseError>


/** Verify constructing a New containerConfig DTRT. */
TEST(LibertineContainerConfigList, constructDefault)
{
  ContainerConfigList container_configs;

  EXPECT_EQ(container_configs.empty(), true);
  EXPECT_EQ(container_configs.size(), 0);
}

/** Verify constructing a ContainerConfig from JSON DTRT. */
TEST(LibertineContainerConfigList, constructFromJson)
{
  QByteArray raw_json(
    "{"
      "\"containerList\": ["
        "{"
          "\"id\":            \"wily\","
          "\"name\":          \"Wily Werewolf\","
          "\"distro\":        \"wily\","
          "\"installedApps\": ["
          "],"
          "\"installStatus\": \"ready\""
        "},"
        "{"
          "\"id\":            \"wily1\","
          "\"name\":          \"Wily Werewolf\","
          "\"distro\":        \"wily\","
          "\"installedApps\": ["
          "],"
          "\"installStatus\": \"new\""
        "}"
      "],"
      "\"defaultContainer\": \"wily\""
    "}"
  );
  QJsonParseError parse_error;
  QJsonDocument json = QJsonDocument::fromJson(raw_json, &parse_error);
  ASSERT_EQ(parse_error.error, 0) << parse_error.errorString().toStdString();

  ContainerConfigList container_configs(json.object());

  EXPECT_EQ(container_configs.empty(), false);
  EXPECT_EQ(container_configs.size(), 2);
  EXPECT_EQ(container_configs.default_container_id().toStdString(), "wily");
}
