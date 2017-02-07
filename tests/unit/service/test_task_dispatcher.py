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
from libertine.service import task_dispatcher


class TestTaskDispatcher(TestCase):
    def setUp(self):
        self._connection = unittest.mock.Mock()
        self._config_patcher = unittest.mock.patch('libertine.service.task_dispatcher.libertine.ContainersConfig.ContainersConfig')
        self._config_patcher.start()
        self._dispatcher = task_dispatcher.TaskDispatcher(self._connection)

    def tearDown(self):
        self._config_patcher.stop()

    def test_search_calls_search_on_container(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.Container') as MockContainer:
            c = MockContainer.return_value
            c.search.return_value = 123
            self.assertEqual(123, self._dispatcher.search('palpatine', 'sith'))
            c.search.assert_called_once_with('sith')

    def test_app_info_calls_app_info_on_container(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.Container') as MockContainer:
            c = MockContainer.return_value
            c.app_info.return_value = 123
            self.assertEqual(123, self._dispatcher.app_info('palpatine', 'deathstar'))
            c.app_info.assert_called_once_with('deathstar')

    def test_install_calls_install_on_container(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.Container') as MockContainer:
            c = MockContainer.return_value
            c.install.return_value = 123
            self.assertEqual(123, self._dispatcher.install('palpatine', 'darkside'))
            c.install.assert_called_once_with('darkside')

    def test_remove_calls_remove_on_container(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.Container') as MockContainer:
            c = MockContainer.return_value
            c.remove.return_value = 123
            self.assertEqual(123, self._dispatcher.remove('palpatine', 'lightside'))
            c.remove.assert_called_once_with('lightside')

    def test_create_calls_create_on_container(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.Container') as MockContainer:
            c = MockContainer.return_value
            c.create.return_value = 123
            self.assertEqual(123, self._dispatcher.create('palpatine', 'Emperor Palpatine', 'zesty', 'lxd', False))
            c.create.assert_called_once_with('Emperor Palpatine', 'zesty', 'lxd', False)

    def test_destroy_calls_destroy_on_container(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.Container') as MockContainer:
            c = MockContainer.return_value
            c.destroy.return_value = 123
            self.assertEqual(123, self._dispatcher.destroy('palpatine'))
            c.destroy.assert_called_once_with()

    def test_update_calls_update_on_container(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.Container') as MockContainer:
            c = MockContainer.return_value
            c.update.return_value = 123
            self.assertEqual(123, self._dispatcher.update('palpatine'))
            c.update.assert_called_once_with()

    def test_list_app_ids_calls_list_app_ids_on_container(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.Container') as MockContainer:
            c = MockContainer.return_value
            c.list_app_ids.return_value = 123
            self.assertEqual(123, self._dispatcher.list_app_ids('palpatine'))
            c.list_app_ids.assert_called_once_with()

    def test_containers_reused_on_subsequent_calls(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.Container') as MockContainer:
            c = MockContainer.return_value
            c.id = 'palpatine'
            self._dispatcher.list_app_ids('palpatine')
            self._dispatcher.list_app_ids('palpatine')
            self._dispatcher.list_app_ids('palpatine')
            MockContainer.assert_called_once_with('palpatine', unittest.mock.ANY, self._connection, unittest.mock.ANY)

    def test_container_callback_removes_container(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.Container') as MockContainer:
            c = MockContainer.return_value
            c.id = 'palpatine'
            self._dispatcher.list_app_ids('palpatine')
            MockContainer.assert_called_once_with('palpatine', unittest.mock.ANY, self._connection, unittest.mock.ANY)
            name, args, kwargs = MockContainer.mock_calls[0]
            args[len(args)-1](MockContainer.return_value)
            self._dispatcher.list_app_ids('palpatine')
            MockContainer.assert_has_calls([ # verify container constructed twice
                unittest.mock.call('palpatine', unittest.mock.ANY, self._connection, unittest.mock.ANY),
                unittest.mock.call('palpatine', unittest.mock.ANY, self._connection, unittest.mock.ANY)
            ], any_order=True)

    def test_container_info_creates_container_info_task(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.ContainerInfoTask') as MockContainerInfoTask:
            task = MockContainerInfoTask.return_value
            task.id = 123
            self.assertEqual(123, self._dispatcher.container_info('palpatine'))
            MockContainerInfoTask.assert_called_once_with('palpatine', [], unittest.mock.ANY, self._connection, unittest.mock.ANY)
            task.start.assert_called_once_with()

    def test_container_info_forwards_container_task_ids(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.ContainerInfoTask') as MockContainerInfoTask:
            task = MockContainerInfoTask.return_value
            with unittest.mock.patch('libertine.service.task_dispatcher.Container') as MockContainer:
                c = MockContainer.return_value
                c.tasks = [1, 2, 3]
                c.id = 'palpatine'
                self._dispatcher.list_app_ids('palpatine') # creates container
                self._dispatcher.container_info('palpatine')
            MockContainerInfoTask.assert_called_once_with('palpatine', [1, 2, 3], unittest.mock.ANY, self._connection, unittest.mock.ANY)
            task.start.assert_called_once_with()

    def test_list_creates_list_task(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.ListTask') as MockListTask:
            task = MockListTask.return_value
            task.id = 123
            self.assertEqual(123, self._dispatcher.list())
            MockListTask.assert_called_once_with(unittest.mock.ANY, self._connection, unittest.mock.ANY)
            task.start.assert_called_once_with()

    def test_containerless_tasks_are_cleaned_up(self):
        with unittest.mock.patch('libertine.service.task_dispatcher.ListTask') as MockListTask:
            self._dispatcher.list()
            MockListTask.assert_called_once_with(unittest.mock.ANY, self._connection, unittest.mock.ANY)
            name, args, kwargs = MockListTask.mock_calls[0]
            self.assertEqual(1, len(self._dispatcher._tasks))
            args[len(args)-1](MockListTask.return_value)
            self.assertEqual(0, len(self._dispatcher._tasks))


if __name__ == '__main__':
    unittest.main()
