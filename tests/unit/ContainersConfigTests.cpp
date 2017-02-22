/*
 * Copyright 2017 Canonical Ltd.
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
#include "common/ContainersConfig.h"

#include <gtest/gtest.h>
#include <QtCore/QByteArray>
#include <QtCore/QJsonArray>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonParseError>


namespace
{
static const QByteArray test_json(R"EOF(
  {
    "containerList": [
      {
        "id":            "xenial-test",
        "name":          "Xenial Xerus",
        "distro":        "xenial",
        "type":          "lxc",
        "installStatus": "ready",
        "installedApps": [
          {
            "appStatus":   "installing",
            "packageName": "0ad"
          },
          {
            "appStatus":   "installed",
            "packageName": "sakura"
          }
        ],
        "extraArchives": [
          {
            "archiveName": "ppa:some/archive",
            "archiveStatus": "installed"
          }
        ],
        "bindMounts": [
          "/media/lrp/PEPPER"
        ]
      },
      {
        "id":            "test-zesty",
        "name":          "Zesty Zapus",
        "distro":        "zesty",
        "type":          "lxd",
        "multiarch":     "enabled",
        "installStatus": "new"
      }
    ],
    "defaultContainer": "xenial"
  })EOF"
);
}


TEST(ContainersConfigTest, emptyConfigFromDefaultConstructor)
{
  ContainersConfig config;

  EXPECT_TRUE(config.default_container.isEmpty());
  EXPECT_TRUE(config.containers.isEmpty());
}


TEST(ContainersConfigTest, loadsContainerInformationFromJson)
{
  QJsonParseError parse_error;
  auto json = QJsonDocument::fromJson(test_json, &parse_error);
  ASSERT_EQ(parse_error.error, 0) << parse_error.errorString().toStdString();

  ContainersConfig config(json.object());

  EXPECT_EQ(config.default_container, "xenial");
  ASSERT_EQ(config.containers.size(), 2);
  EXPECT_EQ(config.containers[0].id, "xenial-test");
  EXPECT_EQ(config.containers[0].name, "Xenial Xerus");
  EXPECT_EQ(config.containers[0].distro, "xenial");
  EXPECT_EQ(config.containers[0].type, "lxc");
  EXPECT_EQ(config.containers[0].multiarch, "disabled");
  EXPECT_EQ(config.containers[0].status, "ready");

  EXPECT_EQ(config.containers[1].id, "test-zesty");
  EXPECT_EQ(config.containers[1].name, "Zesty Zapus");
  EXPECT_EQ(config.containers[1].distro, "zesty");
  EXPECT_EQ(config.containers[1].type, "lxd");
  EXPECT_EQ(config.containers[1].multiarch, "enabled");
  EXPECT_EQ(config.containers[1].status, "new");

  ASSERT_EQ(config.containers[0].installed_apps.size(), 2);
  EXPECT_EQ(config.containers[0].installed_apps[0].name, "0ad");
  EXPECT_EQ(config.containers[0].installed_apps[0].status, "installing");
  EXPECT_EQ(config.containers[0].installed_apps[1].name, "sakura");
  EXPECT_EQ(config.containers[0].installed_apps[1].status, "installed");

  ASSERT_EQ(config.containers[0].archives.size(), 1);
  EXPECT_EQ(config.containers[0].archives[0].status, "installed");
  EXPECT_EQ(config.containers[0].archives[0].name, "ppa:some/archive");

  ASSERT_EQ(config.containers[0].mounts.size(), 1);
  EXPECT_EQ(config.containers[0].mounts[0].path, "/media/lrp/PEPPER");
}


TEST(ContainersConfigTest, dumpsAllDataBackIntoJson)
{
  QJsonParseError parse_error;
  auto json = QJsonDocument::fromJson(test_json, &parse_error).object();
  ASSERT_EQ(parse_error.error, 0) << parse_error.errorString().toStdString();

  auto actual = ContainersConfig(json).dump();

  // Our implementation fills in missing information
  auto xenial = json["containerList"].toArray()[0].toObject();
  xenial["multiarch"] = "disabled";
  auto zesty = json["containerList"].toArray()[1].toObject();
  zesty["installedApps"] = QJsonArray();
  zesty["extraArchives"] = QJsonArray();
  zesty["bindMounts"] = QJsonArray();
  json["containerList"] = QJsonArray{xenial, zesty};

  EXPECT_EQ(json, actual);
}


TEST(ContainersConfigTest, createsDefaultContainer)
{
  ContainersConfig::Container container;
  EXPECT_EQ(container.id, "unknown");
  EXPECT_EQ(container.name, "unknown");
  EXPECT_EQ(container.distro, "unknown");
  EXPECT_EQ(container.type, "unknown");
  EXPECT_EQ(container.multiarch, "disabled");
  EXPECT_EQ(container.status, "unknown");
  EXPECT_TRUE(container.archives.isEmpty());
  EXPECT_TRUE(container.installed_apps.isEmpty());
  EXPECT_TRUE(container.mounts.isEmpty());
}
