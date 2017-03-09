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

#include "liblibertine/libertine.h"
#include <cstdlib>
#include <gio/gio.h>
#include <gtest/gtest.h>
#include <libdbustest/dbus-test.h>
#include <memory>
#include <QtCore/QByteArray>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonParseError>

class LiblibertineTest : public ::testing::Test
{
protected:
  static void SetUpTestCase()
  {
    process = dbus_test_process_new("libertined");
    dbus_test_process_append_param(process, "--debug");

    dbus_test_task_set_bus(DBUS_TEST_TASK(process), DBUS_TEST_SERVICE_BUS_SESSION);
    dbus_test_task_set_name(DBUS_TEST_TASK(process), "libertine");
    dbus_test_task_set_return(DBUS_TEST_TASK(process), DBUS_TEST_TASK_RETURN_IGNORE);
    dbus_test_task_set_wait_finished(DBUS_TEST_TASK(process), FALSE);

    wait = dbus_test_task_new();
    dbus_test_task_set_wait_for(wait, "com.canonical.libertine.Service");

    service = dbus_test_service_new(nullptr);
    dbus_test_service_add_task(service, DBUS_TEST_TASK(process));
    dbus_test_service_add_task(service, wait);

    dbus_test_service_start_tasks(service);

    bus = g_bus_get_sync(G_BUS_TYPE_SESSION, nullptr, nullptr);
    g_dbus_connection_set_exit_on_close(bus, FALSE);
    g_object_add_weak_pointer(G_OBJECT(bus), (gpointer*)&bus);
  }

  static void TearDownTestCase()
  {
    g_clear_object(&process);
    g_clear_object(&wait);

    g_clear_object(&service);
    g_object_unref(bus);
  }

private:
  static DbusTestProcess* process;
  static DbusTestTask* wait;
  static DbusTestService* service;
  static GDBusConnection* bus;
};


DbusTestProcess* LiblibertineTest::process = nullptr;
DbusTestTask* LiblibertineTest::wait = nullptr;
DbusTestService* LiblibertineTest::service = nullptr;
GDBusConnection* LiblibertineTest::bus = nullptr;


TEST_F(LiblibertineTest, libertine_list_containers)
{
  auto scontainers = std::shared_ptr<gchar*>(libertine_list_containers(), g_strfreev);
  auto containers = scontainers.get();

  ASSERT_NE(containers[0], nullptr);
  EXPECT_STREQ(containers[0], "jarjar");

  ASSERT_NE(containers[1], nullptr);
  EXPECT_STREQ(containers[1], "padme");

  ASSERT_NE(containers[2], nullptr);
  EXPECT_STREQ(containers[2], "anakin");

  ASSERT_EQ(containers[3], nullptr);
}


TEST_F(LiblibertineTest, libertine_list_app_ids)
{
  auto sapps = std::shared_ptr<gchar*>(libertine_list_apps_for_container("padme"), g_strfreev);
  auto apps = sapps.get();

  ASSERT_NE(apps[0], nullptr);
  EXPECT_STREQ(apps[0], "padme_dagobah_0.0");

  ASSERT_NE(apps[1], nullptr);
  EXPECT_STREQ(apps[1], "padme_tatooine_0.0");

  ASSERT_EQ(apps[2], nullptr);
}


TEST_F(LiblibertineTest, libertine_container_name)
{
  auto actual = libertine_container_name("padme");
  EXPECT_STREQ("Padme Amedala", actual);
  g_free(actual);
}


TEST_F(LiblibertineTest, libertine_container_path)
{
  auto actual = libertine_container_path("padme");
  auto expected = QString(getenv("XDG_CACHE_HOME")) + "/libertine-container/padme/rootfs";
  EXPECT_STREQ(expected.toUtf8(), actual);
  g_free(actual);
}


TEST_F(LiblibertineTest, libertine_container_path_returns_empty)
{
  EXPECT_EQ(nullptr, libertine_container_path("jarjar"));
}


TEST_F(LiblibertineTest, libertine_container_home_path)
{
  auto actual = libertine_container_home_path("padme");
  auto expected = QString(getenv("XDG_DATA_HOME")) + "/libertine-container/user-data/padme";
  EXPECT_STREQ(expected.toUtf8(), actual);
  g_free(actual);
}


TEST_F(LiblibertineTest, libertine_container_home_path_returns_empty)
{
  EXPECT_EQ(nullptr, libertine_container_home_path("jarjar"));
}
