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


class TestRemoveTask(TestCase):
    def setUp(self):
        self.config      = unittest.mock.create_autospec(ContainersConfig)
        self.connection  = unittest.mock.Mock()
        self.lock      = unittest.mock.MagicMock()
        self.called_with = None

    def callback(self, task):
        self.called_with = task

    def test_sends_error_on_non_installed_package(self):
        self.config.get_package_install_status.return_value = 'installing'
        with unittest.mock.patch('libertine.service.tasks.base_task.libertine.service.progress.Progress') as MockProgress:
            progress = MockProgress.return_value
            task = tasks.RemoveTask('darkside-common', 'palpatine', self.config, self.lock, self.connection, self.callback)
            task._instant_callback = True
            task.start().join()

            progress.error.assert_called_once_with('Package \'darkside-common\' not installed, skipping remove')
            self.assertEqual(task, self.called_with)

    def test_sends_error_on_failed_install(self):
        self.config.get_package_install_status.return_value = 'installed'
        with unittest.mock.patch('libertine.service.tasks.base_task.libertine.service.progress.Progress') as MockProgress:
            progress = MockProgress.return_value
            task = tasks.RemoveTask('darkside-common', 'palpatine', self.config, self.lock, self.connection, self.callback)
            task._instant_callback = True

            with unittest.mock.patch('libertine.service.tasks.remove_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.remove_package.return_value = False
                task.start().join()

            progress.error.assert_called_once_with("Package removal failed for 'darkside-common'")
            self.config.update_package_install_status.assert_has_calls([
                unittest.mock.call('palpatine', 'darkside-common', 'removing'),
                unittest.mock.call('palpatine', 'darkside-common', 'installed')
            ], any_order=True)
            self.assertEqual(task, self.called_with)

    def test_successfully_install(self):
        self.config.get_package_install_status.return_value = 'installed'
        with unittest.mock.patch('libertine.service.tasks.base_task.libertine.service.progress.Progress') as MockProgress:
            progress = MockProgress.return_value
            progress.done = False
            task = tasks.RemoveTask('darkside-common', 'palpatine', self.config, self.lock, self.connection, self.callback)
            task._instant_callback = True

            with unittest.mock.patch('libertine.service.tasks.remove_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.remove_package.return_value = True
                task.start().join()

            progress.finished.assert_called_once_with('palpatine')
            self.config.update_package_install_status.assert_called_once_with('palpatine', 'darkside-common', 'removing')
            self.config.delete_package.assert_called_once_with('palpatine', 'darkside-common')
            self.assertEqual(task, self.called_with)