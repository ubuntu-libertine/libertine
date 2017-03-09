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

import unittest.mock
from unittest import TestCase
from libertine.service import operations_monitor, download


class TestOperationsMonitor(TestCase):
    def setUp(self):
        self._connection = unittest.mock.Mock()

    def test_new_operation_returns_some_id(self):
        with unittest.mock.patch('dbus.service.Object'):
            monitor = operations_monitor.OperationsMonitor(self._connection)
            monitor._connection = self._connection

            with unittest.mock.patch('libertine.service.operations_monitor.download.Download') as MockDownload:
                self.assertIsNotNone(monitor.new_operation())

    def test_remove_connection(self):
        with unittest.mock.patch('dbus.service.Object'):
            monitor = operations_monitor.OperationsMonitor(self._connection)
            monitor._connection = self._connection

            with unittest.mock.patch('libertine.service.operations_monitor.download.Download') as MockDownload:
                monitor.remove_from_connection(monitor.new_operation())
                MockDownload.return_value.remove_from_connection.assert_called_once_with()

    def test_returns_done_for_operation(self):
        with unittest.mock.patch('dbus.service.Object'):
            monitor = operations_monitor.OperationsMonitor(self._connection)
            monitor._connection = self._connection

            with unittest.mock.patch('libertine.service.operations_monitor.download.Download') as MockDownload:
                MockDownload.return_value.done = True
                self.assertTrue(monitor.done(monitor.new_operation()))

                MockDownload.return_value.done = False
                self.assertFalse(monitor.done(monitor.new_operation()))

                # non-existent operation
                self.assertFalse(monitor.done("123456"))

    def test_running_returns_download_state(self):
        with unittest.mock.patch('dbus.service.Object'):
            monitor = operations_monitor.OperationsMonitor(self._connection)
            monitor._connection = self._connection

            with unittest.mock.patch('libertine.service.operations_monitor.download.Download') as MockDownload:
                MockDownload.return_value.done = True
                self.assertFalse(monitor.running(monitor.new_operation()))

                MockDownload.return_value.done = False
                self.assertTrue(monitor.running(monitor.new_operation()))

                # non-existent operation
                self.assertFalse(monitor.running("123456"))

    def test_result_returns_download_results(self):
        with unittest.mock.patch('dbus.service.Object'):
            monitor = operations_monitor.OperationsMonitor(self._connection)
            monitor._connection = self._connection

            with unittest.mock.patch('libertine.service.operations_monitor.download.Download') as MockDownload:
                MockDownload.return_value.result = "pokemongus"
                self.assertEqual("pokemongus", monitor.result(monitor.new_operation()))

                # non-existent operation
                self.assertEqual("", monitor.result("123456"))

    def test_last_error_returns_download_last_errors(self):
        with unittest.mock.patch('dbus.service.Object'):
            monitor = operations_monitor.OperationsMonitor(self._connection)
            monitor._connection = self._connection

            with unittest.mock.patch('libertine.service.operations_monitor.download.Download') as MockDownload:
                MockDownload.return_value.last_error = "pokemongus"
                self.assertEqual("pokemongus", monitor.last_error(monitor.new_operation()))

                # non-existent operation
                self.assertEqual("", monitor.last_error("123456"))

    def test_forwards_finished(self):
        with unittest.mock.patch('dbus.service.Object'):
            monitor = operations_monitor.OperationsMonitor(self._connection)
            monitor._connection = self._connection
            monitor._locations = []

            with unittest.mock.patch('libertine.service.operations_monitor.download.Download') as MockDownload:
                path = monitor.new_operation()
                monitor.finished(path)
                MockDownload.return_value.finished.assert_called_once_with(path)

                # test does not crash on empty
                MockDownload.reset_mock()
                monitor.finished("some/junk")
                MockDownload.return_value.finished.assert_not_called()

    def test_forwards_error(self):
        with unittest.mock.patch('dbus.service.Object'):
            monitor = operations_monitor.OperationsMonitor(self._connection)
            monitor._connection = self._connection
            monitor._locations = []

            with unittest.mock.patch('libertine.service.operations_monitor.download.Download') as MockDownload:
                path = monitor.new_operation()
                monitor.error(path, "something messed up")
                MockDownload.return_value.error.assert_called_once_with("something messed up")

                # test does not crash on empty
                MockDownload.reset_mock()
                monitor.error("some/junk", "something messed up")
                MockDownload.return_value.error.assert_not_called()

    def test_forwards_data(self):
        with unittest.mock.patch('dbus.service.Object'):
            monitor = operations_monitor.OperationsMonitor(self._connection)
            monitor._connection = self._connection
            monitor._locations = []

            with unittest.mock.patch('libertine.service.operations_monitor.download.Download') as MockDownload:
                path = monitor.new_operation()
                monitor.data(path, "some of that gud data")
                MockDownload.return_value.data.assert_called_once_with("some of that gud data")

                # test does not crash on empty
                MockDownload.reset_mock()
                monitor.data("some/junk", "some of that gud data")
                MockDownload.return_value.data.assert_not_called()



if __name__ == '__main__':
    unittest.main()
