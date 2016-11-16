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
from libertine.ContainersConfig import ContainersConfig


class TestAppInfoTask(TestCase):
    def setUp(self):
        self.config     = unittest.mock.create_autospec(ContainersConfig)
        self.cache      = unittest.mock.create_autospec(apt.AptCache)
        self.connection = unittest.mock.Mock()

    def test_app_not_found_causes_error(self):
        self.called_with = None
        def callback(t):
            self.called_with = t

        with unittest.mock.patch('libertine.service.tasks.base_task.libertine.service.progress.Progress') as MockProgress:
            progress = MockProgress.return_value
            self.cache.app_info.return_value = {}
            task = tasks.AppInfoTask('palpatine', self.cache, 'lightside', [1, 2], self.config, self.connection, callback)
            task._instant_callback = True
            task.start().join()

            progress.error.assert_called_once_with('Could not find app info for \'lightside\' in container \'palpatine\'')

            self.assertEqual(task, self.called_with)

    def test_success_sends_data(self):
        self.called_with = None
        def callback(t):
            self.called_with = t

        with unittest.mock.patch('libertine.service.tasks.base_task.libertine.service.progress.Progress') as MockProgress:
            progress = MockProgress.return_value
            progress.done = False

            self.cache.app_info.return_value = {'package': 'darkside-common'}
            self.config.get_package_install_status.return_value = 'installed'
            task = tasks.AppInfoTask('palpatine', self.cache, 'darkside', [1, 2, 3], self.config, self.connection, callback)
            task._instant_callback = True
            task.start().join()

            progress.data.assert_called_once_with(str({'package': 'darkside-common', 'status': 'installed', 'task_ids': [1, 2, 3]}))

            self.assertEqual(task, self.called_with)
