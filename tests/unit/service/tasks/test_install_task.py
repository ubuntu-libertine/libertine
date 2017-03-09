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


class TestInstallTask(TestCase):
    def setUp(self):
        self.config      = unittest.mock.create_autospec(ContainersConfig)
        self.lock        = unittest.mock.MagicMock()
        self.monitor    = unittest.mock.create_autospec(operations_monitor.OperationsMonitor)

        self.monitor.new_operation.return_value = "/com/canonical/libertine/Service/Download/123456"
        self.called_with = None

    def callback(self, task):
        self.called_with = task

    def test_sends_error_on_existing_package(self):
        self.config.package_exists.return_value = True
        task = tasks.InstallTask('darkside-common', 'palpatine', self.config, self.lock, self.monitor, self.callback)
        task._instant_callback = True
        task.start().join()

        self.monitor.error.assert_called_once_with(self.monitor.new_operation.return_value, 'Package \'darkside-common\' already exists, skipping install')
        self.assertEqual(task, self.called_with)

    def test_sends_error_on_failed_install(self):
        self.config.package_exists.return_value = False
        task = tasks.InstallTask('darkside-common', 'palpatine', self.config, self.lock, self.monitor, self.callback)
        task._instant_callback = True

        with unittest.mock.patch('libertine.service.tasks.install_task.LibertineContainer') as MockContainer:
            MockContainer.return_value.install_package.return_value = False
            task.start().join()

        self.monitor.error.assert_called_once_with(self.monitor.new_operation.return_value, "Package installation failed for 'darkside-common'")
        self.config.update_package_install_status.assert_called_once_with('palpatine', 'darkside-common', 'installing')
        self.config.delete_package.assert_called_once_with('palpatine', 'darkside-common')
        self.assertEqual(task, self.called_with)

    def test_successfully_install(self):
        self.config.package_exists.return_value = False
        self.monitor.done.return_value = False
        task = tasks.InstallTask('darkside-common', 'palpatine', self.config, self.lock, self.monitor, self.callback)
        task._instant_callback = True

        with unittest.mock.patch('libertine.service.tasks.install_task.LibertineContainer') as MockContainer:
            MockContainer.return_value.install_package.return_value = True
            task.start().join()

        self.monitor.finished.assert_called_once_with(self.monitor.new_operation.return_value)
        self.config.update_package_install_status.assert_has_calls([
            unittest.mock.call('palpatine', 'darkside-common', 'installing'),
            unittest.mock.call('palpatine', 'darkside-common', 'installed')
        ], any_order=True)
        self.assertEqual(task, self.called_with)
