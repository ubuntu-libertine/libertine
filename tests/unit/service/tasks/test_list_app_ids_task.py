# Copyright 2017 Canonical Ltd.
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
from libertine.service import tasks
from libertine.ContainersConfig import ContainersConfig


class TestListAppIdsTask(TestCase):
    def setUp(self):
        self.config      = unittest.mock.create_autospec(ContainersConfig)
        self.connection  = unittest.mock.Mock()
        self.lock      = unittest.mock.MagicMock()
        self.called_with = None

    def callback(self, task):
        self.called_with = task

    def test_sends_error_on_non_existent_container(self):
        self.config.container_exists.return_value = False
        with unittest.mock.patch('libertine.service.tasks.base_task.libertine.service.progress.Progress') as MockProgress:
            progress = MockProgress.return_value
            task = tasks.ListAppIdsTask('palpatine', self.config, self.connection, self.callback)
            task._instant_callback = True

            with unittest.mock.patch('libertine.service.tasks.list_apps_task.LibertineContainer') as MockContainer:
                task.start().join()

            progress.error.assert_called_once_with('Container \'palpatine\' does not exist, skipping list')
            self.assertEqual(task, self.called_with)

    def test_successfully_lists_apps(self):
        self.config.container_exists.return_value = True
        with unittest.mock.patch('libertine.service.tasks.base_task.libertine.service.progress.Progress') as MockProgress:
            progress = MockProgress.return_value
            progress.done = False
            task = tasks.ListAppIdsTask('palpatine', self.config, self.connection, self.callback)
            task._instant_callback = True

            with unittest.mock.patch('libertine.service.tasks.list_app_ids_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.list_app_ids.return_value = '["palpatine_gedit_0.0","palpatine_xterm_0.0"]'
                task.start().join()

            progress.finished.assert_called_once_with('palpatine')
            progress.data.assert_called_once_with(json.dumps('["palpatine_gedit_0.0","palpatine_xterm_0.0"]'))
            self.assertEqual(task, self.called_with)
