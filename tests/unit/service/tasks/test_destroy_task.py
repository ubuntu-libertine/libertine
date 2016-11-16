# Copyright 2016 Canonical Ltd.
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
from libertine.service import tasks
from libertine.ContainersConfig import ContainersConfig


class TestDestroyTask(TestCase):
    def setUp(self):
        self.config      = unittest.mock.create_autospec(ContainersConfig)
        self.connection  = unittest.mock.Mock()
        self.lock      = unittest.mock.MagicMock()
        self.called_with = None

    def callback(self, task):
        self.called_with = task

    def test_sends_error_on_non_ready_container(self):
        self.config._get_value_by_key.return_value = ''
        with unittest.mock.patch('libertine.service.tasks.base_task.libertine.service.progress.Progress') as MockProgress:
            progress = MockProgress.return_value
            progress.done = False
            task = tasks.DestroyTask('palpatine', self.config, self.lock, self.connection, self.callback)
            task._instant_callback = True

            with unittest.mock.patch('libertine.service.tasks.destroy_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.destroy_libertine_container.return_value = True
                task.start().join()

            progress.error.assert_called_once_with('Container \'palpatine\' does not exist')
            self.assertEqual(task, self.called_with)

    def test_sends_error_on_failed_destroy(self):
        self.config._get_value_by_key.return_value = 'ready'
        with unittest.mock.patch('libertine.service.tasks.base_task.libertine.service.progress.Progress') as MockProgress:
            progress = MockProgress.return_value
            task = tasks.DestroyTask('palpatine', self.config, self.lock, self.connection, self.callback)
            task._instant_callback = True

            with unittest.mock.patch('libertine.service.tasks.destroy_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.destroy_libertine_container.return_value = False
                task.start().join()

            progress.error.assert_called_once_with('Destroying container \'palpatine\' failed')
            self.config.update_container_install_status.assert_has_calls([
                unittest.mock.call('palpatine', 'removing'),
                unittest.mock.call('palpatine', 'ready')
            ], any_order=True)
            self.assertEqual(task, self.called_with)

    def test_successfully_destroys(self):
        self.config._get_value_by_key.return_value = 'ready'
        with unittest.mock.patch('libertine.service.tasks.base_task.libertine.service.progress.Progress') as MockProgress:
            progress = MockProgress.return_value
            progress.done = False
            task = tasks.DestroyTask('palpatine', self.config, self.lock, self.connection, self.callback)
            task._instant_callback = True

            with unittest.mock.patch('libertine.service.tasks.destroy_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.destroy_libertine_container.return_value = True
                task.start().join()

            progress.finished.assert_called_once_with('palpatine')
            self.config.update_container_install_status.assert_called_once_with('palpatine', 'removing')
            self.config.delete_container.assert_called_once_with('palpatine')
            self.assertEqual(task, self.called_with)
