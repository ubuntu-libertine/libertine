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
from libertine.service import tasks, operations_monitor
from libertine.ContainersConfig import ContainersConfig


class TestUpdateTask(TestCase):
    def setUp(self):
        self.config  = unittest.mock.create_autospec(ContainersConfig)
        self.lock    = unittest.mock.MagicMock()
        self.client  = unittest.mock.Mock()
        self.monitor = unittest.mock.create_autospec(operations_monitor.OperationsMonitor)

        self.monitor.new_operation.return_value = "/com/canonical/libertine/Service/Download/123456"
        self.called_with = None

    def callback(self, task):
        self.called_with = task

    def test_sends_error_on_non_existent_container(self):
        self.config.container_exists.return_value = False
        task = tasks.UpdateTask('palpatine', self.config, self.lock, self.monitor, self.client, self.callback)
        task._instant_callback = True

        with unittest.mock.patch('libertine.service.tasks.update_task.LibertineContainer') as MockContainer:
            task.start().join()

        self.monitor.error.assert_called_once_with(self.monitor.new_operation.return_value, 'Container \'palpatine\' does not exist, skipping update')

        self.assertEqual(task, self.called_with)

    def test_sends_error_on_failed_update(self):
        self.config.container_exists.return_value = True
        task = tasks.UpdateTask('palpatine', self.config, self.lock, self.monitor, self.client, self.callback)
        task._instant_callback = True

        with unittest.mock.patch('libertine.service.tasks.update_task.LibertineContainer') as MockContainer:
            MockContainer.return_value.update_libertine_container.return_value = False
            task.start().join()

        self.monitor.error.assert_called_once_with(self.monitor.new_operation.return_value, 'Failed to update container \'palpatine\'')
        self.config.update_container_install_status.assert_has_calls([
            unittest.mock.call('palpatine', 'updating'),
            unittest.mock.call('palpatine', 'ready')
        ], any_order=True)

        self.assertEqual(task, self.called_with)

    def test_successfully_updates(self):
        self.config.container_exists.return_value = True
        self.monitor.done.return_value = False
        task = tasks.UpdateTask('palpatine', self.config, self.lock, self.monitor, self.client, self.callback)
        task._instant_callback = True

        with unittest.mock.patch('libertine.service.tasks.update_task.LibertineContainer') as MockContainer:
            MockContainer.return_value.update_libertine_container.return_value = True
            task.start().join()

        self.monitor.finished.assert_called_once_with(self.monitor.new_operation.return_value)
        self.config.update_container_install_status.assert_has_calls([
            unittest.mock.call('palpatine', 'updating'),
            unittest.mock.call('palpatine', 'ready')
        ], any_order=True)

        self.assertEqual(task, self.called_with)
