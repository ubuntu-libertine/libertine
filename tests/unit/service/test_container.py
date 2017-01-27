# Copyright 2016-2017 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest.mock
from unittest import TestCase
from libertine.service import container
from libertine.service import tasks


class TestContainer(TestCase):
    def setUp(self):
        self._connection = unittest.mock.Mock()
        self._config = unittest.mock.Mock()

    def test_search_creates_search_task(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            cache = MockCache.return_value
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.SearchTask') as MockSearchTask:
                c.search('darkseid')
                MockSearchTask.assert_called_once_with('palpatine', cache, 'darkseid', self._connection, unittest.mock.ANY)
                MockSearchTask.return_value.start.assert_called_once_with()

    def test_app_info_creates_app_info_task(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            cache = MockCache.return_value
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.AppInfoTask') as MockAppInfoTask:
                c.app_info('force')
                MockAppInfoTask.assert_called_once_with('palpatine', cache, 'force', [], self._config, self._connection, unittest.mock.ANY)
                MockAppInfoTask.return_value.start.assert_called_once_with()

    def test_app_info_gets_related_task_info(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            cache = MockCache.return_value
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.InstallTask') as MockInstallTask:
                MockInstallTask.return_value.package = 'darkside'
                MockInstallTask.return_value.matches.return_value = False
                install_task_id = c.install('darkside')
                with unittest.mock.patch('libertine.service.container.RemoveTask') as MockRemoveTask:
                    MockRemoveTask.return_value.package = 'darkside'
                    remove_task_id = c.remove('darkside')
                with unittest.mock.patch('libertine.service.container.AppInfoTask') as MockAppInfoTask:
                    c.app_info('darkside')
                    MockAppInfoTask.assert_called_once_with('palpatine', cache, 'darkside', [install_task_id, remove_task_id],
                                                            self._config, self._connection, unittest.mock.ANY)

    def test_install_creates_install_task(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.InstallTask') as MockInstallTask:
                c.install('force')
                MockInstallTask.assert_called_once_with('force', 'palpatine', self._config, unittest.mock.ANY, self._connection, unittest.mock.ANY)
                MockInstallTask.return_value.start.assert_called_once_with()

    def test_install_only_calls_once_when_unfinished(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.InstallTask') as MockInstallTask:
                c.install('darkside')
                c.install('darkside')
                c.install('darkside')
                MockInstallTask.assert_called_once_with('darkside', 'palpatine', self._config, unittest.mock.ANY, self._connection, unittest.mock.ANY)
                MockInstallTask.return_value.start.assert_called_once_with()

    def test_remove_creates_remove_task(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.RemoveTask') as MockRemoveTask:
                c.remove('force')
                MockRemoveTask.assert_called_once_with('force', 'palpatine', self._config, unittest.mock.ANY, self._connection, unittest.mock.ANY)
                MockRemoveTask.return_value.start.assert_called_once_with()

    def test_remove_only_calls_once_when_unfinished(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.RemoveTask') as MockRemoveTask:
                c.remove('darkside')
                c.remove('darkside')
                c.remove('darkside')
                MockRemoveTask.assert_called_once_with('darkside', 'palpatine', self._config, unittest.mock.ANY, self._connection, unittest.mock.ANY)
                MockRemoveTask.return_value.start.assert_called_once_with()

    def test_create_creates_create_task(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.CreateTask') as MockCreateTask:
                c.create('Emperor Palpatine', 'zesty', 'lxd', False)
                MockCreateTask.assert_called_once_with('palpatine', 'Emperor Palpatine', 'zesty', 'lxd', False,
                                                       self._config, unittest.mock.ANY, self._connection, unittest.mock.ANY)
                MockCreateTask.return_value.start.assert_called_once_with()

    def test_create_only_calls_once_when_unfinished(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.CreateTask') as MockCreateTask:
                c.create('Emperor Palpatine', 'zesty', 'lxd', False)
                c.create('Emperor Palpatine', 'zesty', 'lxd', False)
                c.create('Emperor Palpatine', 'zesty', 'lxd', False)
                MockCreateTask.assert_called_once_with('palpatine', 'Emperor Palpatine', 'zesty', 'lxd', False,
                                                       self._config, unittest.mock.ANY, self._connection, unittest.mock.ANY)
                MockCreateTask.return_value.start.assert_called_once_with()

    def test_destroy_creates_destroy_task(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.DestroyTask') as MockDestroyTask:
                c.destroy()
                MockDestroyTask.assert_called_once_with('palpatine', self._config, unittest.mock.ANY, self._connection, unittest.mock.ANY)
                MockDestroyTask.return_value.start.assert_called_once_with()

    def test_destroy_only_calls_once_when_unfinished(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.DestroyTask') as MockDestroyTask:
                c.destroy()
                c.destroy()
                c.destroy()
                MockDestroyTask.assert_called_once_with('palpatine', self._config, unittest.mock.ANY, self._connection, unittest.mock.ANY)
                MockDestroyTask.return_value.start.assert_called_once_with()

    def test_update_creates_update_task(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.UpdateTask') as MockUpdateTask:
                c.update()
                MockUpdateTask.assert_called_once_with('palpatine', self._config, unittest.mock.ANY, self._connection, unittest.mock.ANY)
                MockUpdateTask.return_value.start.assert_called_once_with()

    def test_update_only_calls_once_when_unfinished(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.UpdateTask') as MockUpdateTask:
                c.update()
                c.update()
                c.update()
                MockUpdateTask.assert_called_once_with('palpatine', self._config, unittest.mock.ANY, self._connection, unittest.mock.ANY)
                MockUpdateTask.return_value.start.assert_called_once_with()

    def test_list_apps_creates_list_apps_task(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.ListAppsTask') as MockListAppsTask:
                c.list_apps()
                MockListAppsTask.assert_called_once_with('palpatine', self._config, self._connection, unittest.mock.ANY)
                MockListAppsTask.return_value.start.assert_called_once_with()

    def test_list_app_ids_creates_list_app_ids_task(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.ListAppIdsTask') as MockListAppsTask:
                c.list_app_ids()
                MockListAppsTask.assert_called_once_with('palpatine', self._config, self._connection, unittest.mock.ANY)
                MockListAppsTask.return_value.start.assert_called_once_with()

    def test_removes_task_during_callback(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            c = container.Container('palpatine', self._config, self._connection, lambda task: task)
            with unittest.mock.patch('libertine.service.container.InstallTask') as MockInstallTask:
                MockInstallTask.return_value.package = 'force'
                c.install('force')
                self.assertEqual(1, len(MockInstallTask.return_value.start.mock_calls)) # ensure initial mocks were called
                c.install('force')
                self.assertEqual(1, len(MockInstallTask.return_value.start.mock_calls)) # ensure no more mocks were called
                name, args, kwargs = MockInstallTask.mock_calls[0]
                args[len(args)-1](MockInstallTask.return_value.start.return_value)
                c.install('force')
                self.assertEqual(2, len(MockInstallTask.return_value.start.mock_calls)) # ensure mocks were called again

    def test_completing_all_tasks_fires_callback(self):
        with unittest.mock.patch('libertine.service.container.apt.AptCache') as MockCache:
            self._container_id = None
            def callback(container):
                self._container_id = container.id
            c = container.Container('palpatine', self._config, self._connection, callback)
            with unittest.mock.patch('libertine.service.container.InstallTask') as MockInstallTask:
                c.install('force')
                name, args, kwargs = MockInstallTask.mock_calls[0]
                args[len(args)-1](MockInstallTask.return_value)
            self.assertEqual('palpatine', self._container_id)


if __name__ == '__main__':
    unittest.main()
