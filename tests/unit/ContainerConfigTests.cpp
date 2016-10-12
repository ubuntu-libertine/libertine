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

#include "common/ContainerConfig.h"
#include <QtCore/QByteArray>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonParseError>


/** Verify constructing a New containerConfig DTRT. */
TEST(LibertineContainerConfig, constructFromScalars)
{
  ContainerConfig container_config("id", "name", "type", "distro");

  EXPECT_EQ(container_config.container_id(),   "id");
  EXPECT_EQ(container_config.name(),           "name");
  EXPECT_EQ(container_config.container_type(), "type");
  EXPECT_EQ(container_config.distro_series(),  "distro");
  EXPECT_EQ(container_config.install_status(), "new");
}

/** Verify constructing a ContainerConfig from JSON DTRT. */
TEST(LibertineContainerConfig, constructFromJson)
{
  QByteArray raw_json(
    "{"
        "\"id\":            \"wily3\","
        "\"name\":          \"Wily Werewolf\","
        "\"type\":          \"lxc\","
        "\"distro\":        \"wily\","
        "\"installedApps\": ["
        "],"
        "\"installStatus\": \"ready\""
    "}"
  );
  QJsonParseError parse_error;
  QJsonDocument json = QJsonDocument::fromJson(raw_json, &parse_error);
  ASSERT_EQ(parse_error.error, 0) << parse_error.errorString().toStdString();

  ContainerConfig container_config(json.object());

  EXPECT_EQ(container_config.container_id().toStdString(),   "wily3");
  EXPECT_EQ(container_config.name().toStdString(),           "Wily Werewolf");
  EXPECT_EQ(container_config.distro_series().toStdString(),  "wily");
  EXPECT_EQ(container_config.install_status(), "ready");
  EXPECT_EQ(container_config.container_apps().empty(), true);
}

TEST(LibertineContainerConfig, constructFromJsonWithOneApp)
{
  QByteArray raw_json(
    "{"
        "\"id\":            \"wily3\","
        "\"name\":          \"Wily Werewolf\","
        "\"type\":          \"lxc\","
        "\"distro\":        \"wily\","
        "\"installedApps\": ["
            "{"
                 "\"packageName\": \"firefox\","
                 "\"appStatus\":   \"installed\""
            "}"
        "],"
        "\"installStatus\": \"ready\""
    "}"
  );
  QJsonParseError parse_error;
  QJsonDocument json = QJsonDocument::fromJson(raw_json, &parse_error);
  ASSERT_EQ(parse_error.error, 0) << parse_error.errorString().toStdString();

  ContainerConfig container_config(json.object());

  EXPECT_EQ(container_config.container_apps().empty(), false);
  EXPECT_EQ(container_config.container_apps()[0]->package_name(), "firefox");
  EXPECT_EQ(container_config.container_apps()[0]->app_status(), "installed");
}

TEST(LibertineContainerConfig, constructFromJsonWithTwoApps)
{
  QByteArray raw_json(
    "{"
        "\"id\":            \"wily3\","
        "\"name\":          \"Wily Werewolf\","
        "\"type\":          \"lxc\","
        "\"distro\":        \"wily\","
        "\"installedApps\": ["
            "{"
                 "\"packageName\": \"firefox\","
                 "\"appStatus\":   \"installed\""
            "},"
            "{"
                 "\"packageName\": \"xterm\","
                 "\"appStatus\":   \"new\""
            "}"
        "],"
        "\"installStatus\": \"ready\""
    "}"
  );
  QJsonParseError parse_error;
  QJsonDocument json = QJsonDocument::fromJson(raw_json, &parse_error);
  ASSERT_EQ(parse_error.error, 0) << parse_error.errorString().toStdString();

  ContainerConfig container_config(json.object());

  EXPECT_EQ(container_config.container_apps().empty(), false);
  EXPECT_EQ(container_config.container_apps()[0]->package_name(), "firefox");
  EXPECT_EQ(container_config.container_apps()[0]->app_status(), "installed");
  EXPECT_EQ(container_config.container_apps()[1]->package_name(), "xterm");
  EXPECT_EQ(container_config.container_apps()[1]->app_status(), "new");
}
