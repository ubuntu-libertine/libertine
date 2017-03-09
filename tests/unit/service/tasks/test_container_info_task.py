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


import ast
import unittest.mock
from unittest import TestCase
from libertine import utils
from libertine.service import tasks, operations_monitor
from libertine.ContainersConfig import ContainersConfig


class TestContainerInfoTask(TestCase):
    def setUp(self):
        self.config   = unittest.mock.create_autospec(ContainersConfig)
        self.monitor  = unittest.mock.create_autospec(operations_monitor.OperationsMonitor)
        self.monitor.new_operation.return_value = "/com/canonical/libertine/Service/Download/123456"

    def test_success_sends_data(self):
        self.called_with = None
        def callback(t):
            self.called_with = t

        self.monitor.done.return_value = False

        self.config.get_container_install_status.return_value = 'ready'
        self.config.get_container_name.return_value = 'Palpatine'
        task = tasks.ContainerInfoTask('palpatine', [1, 2, 3], self.config, self.monitor, callback)
        task._instant_callback = True
        task.start().join()

        self.monitor.data.assert_called_once_with(self.monitor.new_operation.return_value, unittest.mock.ANY)
        args, kwargs = self.monitor.data.call_args
        self.assertEqual({'id': 'palpatine',
                          'status': 'ready',
                          'task_ids': [1, 2, 3],
                          'name': 'Palpatine',
                          'root': utils.get_libertine_container_rootfs_path('palpatine'),
                          'home': utils.get_libertine_container_home_dir('palpatine')},
                    ast.literal_eval(args[1]))

        self.monitor.finished.assert_called_once_with(self.monitor.new_operation.return_value)

        self.assertEqual(task, self.called_with)
