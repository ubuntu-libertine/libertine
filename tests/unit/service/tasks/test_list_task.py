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


import json
import unittest.mock

from unittest import TestCase
from libertine.service import tasks, operations_monitor
from libertine.ContainersConfig import ContainersConfig


class TestListTask(TestCase):
    def setUp(self):
        self.config     = unittest.mock.create_autospec(ContainersConfig)
        self.monitor    = unittest.mock.create_autospec(operations_monitor.OperationsMonitor)
        self.monitor.new_operation.return_value = "/com/canonical/libertine/Service/Download/123456"

    def test_success_sends_data(self):
        self.called_with = None
        def callback(t):
            self.called_with = t

        self.monitor.done.return_value = False

        task = tasks.ListTask(self.config, self.monitor, callback)
        task._instant_callback = True

        self.config.get_containers.return_value = ['palatine', 'vader', 'maul']
        task.start().join()

        self.monitor.data.assert_called_once_with(self.monitor.new_operation.return_value, json.dumps(['palatine', 'vader', 'maul']))
        self.monitor.finished.assert_called_once_with(self.monitor.new_operation.return_value)

        self.assertEqual(task, self.called_with)
