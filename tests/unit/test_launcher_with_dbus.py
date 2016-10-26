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

import dbus
import dbusmock
import os
import subprocess

from libertine import launcher

from testtools import TestCase
from testtools.matchers import Equals, Contains
from unittest.mock import patch



class MockDBusServer(object):
    """
    A mock object that proxies a mock D-Bus server, for testing things that do
    D-Bus operations in the background.
    """

    def __init__(self, maliit_server_address):
        dbusmock.DBusTestCase.start_session_bus()
        self.maliit_server_address = maliit_server_address
        self._dbus_connection = dbusmock.DBusTestCase.get_dbus(system_bus=False)

    def setUp(self):
        self._dbus_mock_server = dbusmock.DBusTestCase.spawn_server(
                'org.maliit.server',
                '/org/maliit/server/address',
                'org.maliit.Server.Address',
                system_bus=False,
                stdout=subprocess.PIPE)
        self._mock_interface = self._get_mock_interface()
        self._mock_interface.AddProperty('', 'address', self.maliit_server_address)

    def cleanUp(self):
        self._dbus_mock_server.terminate()
        self._dbus_mock_server.wait()

    def getDetails(self):
        return { }

    def _get_mock_interface(self):
        return dbus.Interface(
                self._dbus_connection.get_object(
                    'org.maliit.server',
                    '/org/maliit/server/address',
                    'org.maliit.Server.Address'),
                dbusmock.MOCK_IFACE)


class TestLauncherConfigUsingDBus(TestCase):
    """
    Verifies the defined behaviour of the Libertine Launcher Config class with
    reference to a D-Bus server.
    """
    def setUp(self):
        """
        Need to save and restore the os.environ for each test in case they
        change things.  That's a global that propagates between tests.
        """
        super().setUp()
        fake_maliit_host_address = 'unix:abstract=/tmp/maliit-host-socket'
        self._dbus_server = self.useFixture(MockDBusServer(maliit_server_address=fake_maliit_host_address))
        self._cli = [ self.getUniqueString(), self.getUniqueString() ]

    def test_maliit_socket_bridge_from_dbus(self):
        """
        Make sure the Maliit socket bridge gets configured.

        The Maliit service advertizes it's socket on the D-Bus, although the
        environment variable, if present, overrides that so to test the D-Bus
        advert the environment variable must be clear.
        """
        maliit_bridge = None
        with patch.dict('os.environ'):
            if 'MALIIT_SERVER_ADDRESS' in os.environ:
                del os.environ['MALIIT_SERVER_ADDRESS']

            config = launcher.Config(self._cli[:])

            for bridge in config.socket_bridges:
                if bridge.env_var == 'MALIIT_SERVER_ADDRESS':
                    maliit_bridge = bridge

            self.assertIsNotNone(maliit_bridge)
            self.assertThat(maliit_bridge.host_address, Equals(self._dbus_server.maliit_server_address))
            self.assertThat(maliit_bridge.session_address, Contains('maliit'))
            self.assertThat(maliit_bridge.session_address, Contains(config.id))

