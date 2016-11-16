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
from libertine.service import tasks, apt


class TestSearchTask(TestCase):
    def setUp(self):
        self.connection  = unittest.mock.Mock()
        self.lock      = unittest.mock.MagicMock()
        self.cache     = unittest.mock.create_autospec(apt.AptCache)
        self.called_with = None

    def callback(self, task):
        self.called_with = task

    def test_successfully_lists_apps(self):
        with unittest.mock.patch('libertine.service.tasks.base_task.libertine.service.progress.Progress') as MockProgress:
            progress = MockProgress.return_value
            progress.done = False
            task = tasks.SearchTask('palpatine', self.cache, 'jarjar', self.connection, self.callback)
            task._instant_callback = True

            self.cache.search.return_value = ['jarjar', 'sidius']
            task.start().join()

            progress.finished.assert_called_once_with('palpatine')
            progress.data.assert_called_once_with(str(['jarjar', 'sidius']))
            self.assertEqual(task, self.called_with)
