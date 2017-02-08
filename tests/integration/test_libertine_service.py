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
import dbus
import dbus.mainloop.glib
import os
import pexpect
import sys
import tempfile
import threading
import time
import unittest.mock

from gi.repository import GLib
from gi.repository import GObject
from libertine import utils
from libertine.service import tasks, apt
from libertine.ContainersConfig import ContainersConfig
from subprocess import Popen, PIPE
from unittest import TestCase


class TestLibertineService(TestCase):
    _process = None
    _loop = None
    _tempdir = None
    _thread = None

    @classmethod
    def setUpClass(cls):
        cls._tempdir = tempfile.TemporaryDirectory()

        environ = os.environ.copy()
        environ['XDG_DATA_HOME'] = cls._tempdir.name

        cls._process = pexpect.spawnu('libertined --debug', env=environ)
        cls._process.logfile = sys.stdout

        # give libertined enough time to start the whole process
        verbosity = environ.get('LIBERTINE_DEBUG', '1')
        if verbosity == '1':
            cls._process.expect(['.+\n', pexpect.TIMEOUT], timeout=1)
        elif environ['LIBERTINE_DEBUG'] == '2':
            cls._process.expect(['.+\n.+\n.+\n', pexpect.TIMEOUT], timeout=1)

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        cls._loop = GObject.MainLoop()

        cls._thread = threading.Thread(target=cls._loop.run)
        cls._thread.start()

    @classmethod
    def tearDownClass(cls):
        cls._loop.quit()
        cls._process.close()
        cls._tempdir.cleanup()

    def setUp(self):
        self.error = None
        self.result = None
        self.event = threading.Event()

        for retries in range(1, 11):
            try:
                self._bus =  dbus.SessionBus()
                self._libertined = self._bus.get_object('com.canonical.libertine.Service', '/Manager')
                break
            except dbus.DBusException as e:
                print("Service not available (attempt %i/10). Exception: %s" % (retries, str(e)))
                if retries == 10:
                    self.fail('Too many retries. D-bus service connection failed.')
                time.sleep(.1)
            except Exception as e:
                self.fail('Exception occurred during connection: %s' % str(e))

    def _finished_handler(self, path):
        self.event.set()

    def _data_handler(self, message):
        self.result = message

    def _error_handler(self, message):
        self.error = message
        self.event.set()

    def _send(self, func):
        self.event.clear()
        self.result = None

        obj_path = func()
        signals = []
        signals.append(self._bus.add_signal_receiver(path=obj_path, handler_function=self._finished_handler,
                                dbus_interface='com.canonical.applications.Download', signal_name='finished'))
        signals.append(self._bus.add_signal_receiver(path=obj_path, handler_function=self._data_handler,
                                 dbus_interface='com.canonical.libertine.Service.Progress', signal_name='data'))
        signals.append(self._bus.add_signal_receiver(path=obj_path, handler_function=self._error_handler,
                                 dbus_interface='com.canonical.applications.Download', signal_name='error'))

        task = self._bus.get_object('com.canonical.libertine.Service', obj_path)
        if task.running():
            self.event.wait(5)
            self.assertIsNone(self.error)

        self.assertEqual('', task.last_error())
        self.result = task.result()

        for signal in signals:
            self._bus._clean_up_signal_match(signal)

        return self.result

    def test_container_management(self):
        try:
            self.assertEqual([], ast.literal_eval(self._send(lambda: self._libertined.list())))
            self._send(lambda: self._libertined.create('rey', 'Rey', 'xenial', 'mock'))
            self.assertEqual(['rey'], ast.literal_eval(self._send(lambda: self._libertined.list())))

            self._send(lambda: self._libertined.create('kylo', 'Kylo Ren', 'xenial', 'mock'))
            self.assertEqual(['rey', 'kylo'], ast.literal_eval(self._send(lambda: self._libertined.list())))

            self._send(lambda: self._libertined.update('kylo'))

            self.assertEqual({'id': 'rey',
                              'status': 'ready',
                              'name': 'Rey',
                              'task_ids': [],
                              'root': utils.get_libertine_container_rootfs_path('rey'),
                              'home': '{}/libertine-container/user-data/rey'.format(TestLibertineService._tempdir.name)
                             }, ast.literal_eval(self._send(lambda: self._libertined.container_info('rey'))))

            self._send(lambda: self._libertined.destroy('kylo'))
            self.assertEqual(['rey'], ast.literal_eval(self._send(lambda: self._libertined.list())))
        except AssertionError as e:
            raise
        except Exception as e:
            self.fail('Exception thrown in test: %s' % str(e))

    def test_package_management(self):
        try:
            # since we won't actually install/remove packages, we'll
            # verify that our db has been updated correctly
            os.environ['XDG_DATA_HOME'] = TestLibertineService._tempdir.name
            config = ContainersConfig()

            self._send(lambda: self._libertined.create('jarjar', 'JarJar Binks', 'xenial', 'mock'))
            self.assertEqual([], ast.literal_eval(self._send(lambda: self._libertined.list_app_ids('jarjar'))))

            self._send(lambda: self._libertined.install('jarjar', 'the-force'))
            config.refresh_database()
            self.assertEqual('installed', config.get_package_install_status('jarjar', 'the-force'))

            self._send(lambda: self._libertined.install('jarjar', 'gungan-smash'))
            config.refresh_database()
            self.assertEqual('installed', config.get_package_install_status('jarjar', 'gungan-smash'))

            self._send(lambda: self._libertined.remove('jarjar', 'the-force'))
            config.refresh_database()
            self.assertIsNone(config.get_package_install_status('jarjar', 'the-force'))
        except AssertionError as e:
            raise
        except Exception as e:
            self.fail('Exception thrown in test: %s' % str(e))

    def test_app_discovery(self):
        try:
            search_result = ast.literal_eval(self._send(lambda: self._libertined.search('jarjar', 'liblibertine1')))
            self.assertTrue(len(search_result) > 0)

            expected_info_result = search_result[0]
            expected_info_result['status'] = ''
            expected_info_result['task_ids'] = []
            info_result = self._send(lambda: self._libertined.app_info('jarjar', expected_info_result['package']))
            self.assertEqual(expected_info_result, ast.literal_eval(info_result))
        except AssertionError as e:
            raise
        except Exception as e:
            self.fail('Exception thrown in test: %s' % str(e))


if __name__ == '__main__':
    unittest.main()
