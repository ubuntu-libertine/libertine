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


class TestCreateTask(TestCase):
    def setUp(self):
        self.config  = unittest.mock.create_autospec(ContainersConfig)
        self.lock    = unittest.mock.MagicMock()
        self.monitor = unittest.mock.create_autospec(operations_monitor.OperationsMonitor)

        self.monitor.new_operation.return_value = "/com/canonical/libertine/Service/Download/123456"
        self.called_with = None

    def callback(self, task):
        self.called_with = task

    def test_success_creates_lxc_container(self):
        self.config.container_exists.return_value = False
        self.monitor.done.return_value = False
        task = tasks.CreateTask('palpatine', 'Emperor Palpatine', 'zesty', 'lxc', False, self.config, self.lock, self.monitor, self.callback)
        task._instant_callback = True

        with unittest.mock.patch('libertine.service.tasks.create_task.HostInfo') as MockHostInfo:
            MockHostInfo.return_value.is_distro_valid.return_value = True
            MockHostInfo.return_value.has_lxc_support.return_value = True

            with unittest.mock.patch('libertine.service.tasks.create_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.create_libertine_container.return_value = True
                task.start().join()

        self.monitor.finished.assert_called_once_with(self.monitor.new_operation.return_value)
        self.config.add_new_container.assert_called_once_with('palpatine', 'Emperor Palpatine', 'lxc', 'zesty')
        self.config.update_container_install_status.assert_has_calls([
            unittest.mock.call('palpatine', 'installing'),
            unittest.mock.call('palpatine', 'ready')
        ], any_order=True)
        self.assertEqual(task, self.called_with)

    def test_success_creates_chroot_container(self):
        self.config.container_exists.return_value = False
        self.monitor.done.return_value = False
        task = tasks.CreateTask('palpatine', 'Emperor Palpatine', 'zesty', 'chroot', False, self.config, self.lock, self.monitor, self.callback)
        task._instant_callback = True

        with unittest.mock.patch('libertine.service.tasks.create_task.HostInfo') as MockHostInfo:
            MockHostInfo.return_value.is_distro_valid.return_value = True

            with unittest.mock.patch('libertine.service.tasks.create_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.create_libertine_container.return_value = True
                task.start().join()

        self.monitor.finished.assert_called_once_with(self.monitor.new_operation.return_value)
        self.config.add_new_container.assert_called_once_with('palpatine', 'Emperor Palpatine', 'chroot', 'zesty')
        self.config.update_container_install_status.assert_has_calls([
            unittest.mock.call('palpatine', 'installing'),
            unittest.mock.call('palpatine', 'ready')
        ], any_order=True)
        self.assertEqual(task, self.called_with)

    def test_container_runtime_error_sends_error(self):
        self.config.container_exists.return_value = False
        task = tasks.CreateTask('palpatine', 'Emperor Palpatine', 'zesty', 'lxc', False, self.config, self.lock, self.monitor, self.callback)
        task._instant_callback = True

        with unittest.mock.patch('libertine.service.tasks.create_task.HostInfo') as MockHostInfo:
            MockHostInfo.return_value.is_distro_valid.return_value = True
            MockHostInfo.return_value.has_lxc_support.return_value = True

            with unittest.mock.patch('libertine.service.tasks.create_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.create_libertine_container.side_effect = RuntimeError('a great disturbance')
                task.start().join()

        self.monitor.error.assert_called_once_with(self.monitor.new_operation.return_value, 'a great disturbance')

        self.config.add_new_container.assert_called_once_with('palpatine', 'Emperor Palpatine', 'lxc', 'zesty')
        self.config.update_container_install_status.assert_called_once_with('palpatine', 'installing')
        self.config.delete_container.assert_called_once_with('palpatine')

        self.assertEqual(task, self.called_with)

    def test_failed_container_exists_sends_error(self):
        self.config.container_exists.return_value = True
        task = tasks.CreateTask('palpatine', 'Emperor Palpatine', 'zesty', 'lxc', False, self.config, self.lock, self.monitor, self.callback)
        task._instant_callback = True
        task.start().join()

        self.monitor.error.assert_called_once_with(self.monitor.new_operation.return_value, 'Container \'palpatine\' already exists')
        self.assertEqual(task, self.called_with)

    def test_container_invalid_distro_error_sends_error(self):
        self.config.container_exists.return_value = False
        with unittest.mock.patch('libertine.service.tasks.create_task.HostInfo') as MockHostInfo:
            MockHostInfo.return_value.is_distro_valid.return_value = False
            task = tasks.CreateTask('palpatine', 'Emperor Palpatine', 'vesty', 'lxc', False, self.config, self.lock, self.monitor, self.callback)
            task._instant_callback = True
            task.start().join()

        self.monitor.error.assert_called_once_with(self.monitor.new_operation.return_value, 'Invalid distro \'vesty\'.')
        self.assertEqual(task, self.called_with)

    def test_container_improper_lxc_error_sends_error(self):
        self.config.container_exists.return_value = False
        with unittest.mock.patch('libertine.service.tasks.create_task.HostInfo') as MockHostInfo:
            MockHostInfo.return_value.is_distro_valid.return_value = True
            MockHostInfo.return_value.has_lxc_support.return_value = False
            task = tasks.CreateTask('palpatine', 'Emperor Palpatine', 'zesty', 'lxc', False, self.config, self.lock, self.monitor, self.callback)
            task._instant_callback = True
            task.start().join()

        self.monitor.error.assert_called_once_with(self.monitor.new_operation.return_value, \
                'System kernel does not support lxc type containers. Please either use chroot or leave empty.')
        self.assertEqual(task, self.called_with)

    def test_sets_generic_name_when_empty(self):
        self.config.container_exists.return_value = False
        self.monitor.done.return_value = False
        task = tasks.CreateTask('palpatine', None, 'zesty', 'chroot', False, self.config, self.lock, self.monitor, self.callback)
        task._instant_callback = True

        with unittest.mock.patch('libertine.service.tasks.create_task.HostInfo') as MockHostInfo:
            MockHostInfo.return_value.is_distro_valid.return_value = True
            MockHostInfo.return_value.get_distro_codename.return_value = 'Zesty Zapus 17.04'

            with unittest.mock.patch('libertine.service.tasks.create_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.create_libertine_container.return_value = True
                task.start().join()

        self.monitor.finished.assert_called_once_with(self.monitor.new_operation.return_value)
        self.config.add_new_container.assert_called_once_with('palpatine', 'Ubuntu \'Zesty Zapus 17.04\'', 'chroot', 'zesty')
        self.config.update_container_install_status.assert_has_calls([
            unittest.mock.call('palpatine', 'installing'),
            unittest.mock.call('palpatine', 'ready')
        ], any_order=True)
        self.assertEqual(task, self.called_with)

    def test_sets_multiarch(self):
        self.config.container_exists.return_value = False
        self.monitor.done.return_value = False
        task = tasks.CreateTask('palpatine', 'Emperor Palpatine', 'zesty', 'chroot', True, self.config, self.lock, self.monitor, self.callback)
        task._instant_callback = True

        with unittest.mock.patch('libertine.service.tasks.create_task.HostInfo') as MockHostInfo:
            MockHostInfo.return_value.is_distro_valid.return_value = True

            with unittest.mock.patch('libertine.service.tasks.create_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.create_libertine_container.return_value = True
                task.start().join()

        self.monitor.finished.assert_called_once_with(self.monitor.new_operation.return_value)
        self.config.add_new_container.assert_called_once_with('palpatine', 'Emperor Palpatine', 'chroot', 'zesty')
        self.config.update_container_multiarch_support.assert_called_once_with('palpatine', 'enabled')
        self.config.update_container_install_status.assert_has_calls([
            unittest.mock.call('palpatine', 'installing'),
            unittest.mock.call('palpatine', 'ready')
        ], any_order=True)
        self.assertEqual(task, self.called_with)

    def test_sets_default_type(self):
        self.config.container_exists.return_value = False
        self.monitor.done.return_value = False
        task = tasks.CreateTask('palpatine', 'Emperor Palpatine', 'zesty', None, False, self.config, self.lock, self.monitor, self.callback)
        task._instant_callback = True

        with unittest.mock.patch('libertine.service.tasks.create_task.HostInfo') as MockHostInfo:
            MockHostInfo.return_value.is_distro_valid.return_value = True
            MockHostInfo.return_value.select_container_type_by_kernel.return_value = 'lxc'

            with unittest.mock.patch('libertine.service.tasks.create_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.create_libertine_container.return_value = True
                task.start().join()

        self.monitor.finished.assert_called_once_with(self.monitor.new_operation.return_value)
        self.config.add_new_container.assert_called_once_with('palpatine', 'Emperor Palpatine', 'lxc', 'zesty')
        self.config.update_container_install_status.assert_has_calls([
            unittest.mock.call('palpatine', 'installing'),
            unittest.mock.call('palpatine', 'ready')
        ], any_order=True)
        self.assertEqual(task, self.called_with)

    def test_sets_default_distro(self):
        self.config.container_exists.return_value = False
        self.monitor.done.return_value = False
        task = tasks.CreateTask('palpatine', 'Emperor Palpatine', None, 'lxc', False, self.config, self.lock, self.monitor, self.callback)
        task._instant_callback = True

        with unittest.mock.patch('libertine.service.tasks.create_task.HostInfo') as MockHostInfo:
            MockHostInfo.return_value.has_lxc_support.return_value = True
            MockHostInfo.return_value.get_host_distro_release.return_value = 'zesty'

            with unittest.mock.patch('libertine.service.tasks.create_task.LibertineContainer') as MockContainer:
                MockContainer.return_value.create_libertine_container.return_value = True
                task.start().join()

        self.monitor.finished.assert_called_once_with(self.monitor.new_operation.return_value)
        self.config.add_new_container.assert_called_once_with('palpatine', 'Emperor Palpatine', 'lxc', 'zesty')
        self.config.update_container_install_status.assert_has_calls([
            unittest.mock.call('palpatine', 'installing'),
            unittest.mock.call('palpatine', 'ready')
        ], any_order=True)
        self.assertEqual(task, self.called_with)
