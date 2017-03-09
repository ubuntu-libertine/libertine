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
from libertine.service import tasks, apt, operations_monitor


class TestSearchTask(TestCase):
    def setUp(self):
        self.lock      = unittest.mock.MagicMock()
        self.cache     = unittest.mock.create_autospec(apt.AptCache)
        self.monitor    = unittest.mock.create_autospec(operations_monitor.OperationsMonitor)

        self.monitor.new_operation.return_value = "/com/canonical/libertine/Service/Download/123456"
        self.called_with = None

    def callback(self, task):
        self.called_with = task

    def test_successfully_lists_apps(self):
            self.monitor.done.return_value = False
            task = tasks.SearchTask('palpatine', self.cache, 'jarjar', self.monitor, self.callback)
            task._instant_callback = True

            self.cache.search.return_value = ['jarjar', 'sidius']
            task.start().join()

            self.monitor.finished.assert_called_once_with(self.monitor.new_operation.return_value)
            self.monitor.data.assert_called_once_with(self.monitor.new_operation.return_value, str(['jarjar', 'sidius']))
            self.assertEqual(task, self.called_with)
