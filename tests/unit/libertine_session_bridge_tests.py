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

import os
import tempfile
from socket import *
import shutil

from libertine import LibertineSessionBridge, HostSessionSocketPair, SessionSocket, LibertineApplication
from libertine import Socket
from multiprocessing import Process

from testtools import TestCase
from testtools.matchers import Equals, NotEquals

import time
import threading

class TestLibertineSessionBridge(TestCase):
    def setUp(self):
        super(TestLibertineSessionBridge, self).setUp()

        xdg_runtime_path = tempfile.mkdtemp()

        self.addCleanup(self.cleanup)

        # Set necessary enviroment variables
        os.environ['XDG_RUNTIME_DIR'] = xdg_runtime_path

        # Create r/w fake temp sockets, the session will be created by the lsb
        self.host_path    = os.path.join(xdg_runtime_path, 'HOST')
        self.session_path = os.path.join(xdg_runtime_path, 'SESSION')

        self.host_socket = SessionSocket(self.host_path)
        self.assertTrue(os.path.exists(self.host_path))

    """
    Make sure we assert out socket is cleaned up. If we are failing here RAII
    is broken.
    """
    def cleanup(self):
        self.host_socket = None

        self.assertFalse(os.path.exists(self.session_path))
        self.assertFalse(os.path.exists(self.host_path))
        shutil.rmtree(os.environ['XDG_RUNTIME_DIR'])

    """
    A function used to just read from the host socket. In a different thread
    """
    def host_read(self, expected_bytes):
        conn, addr = self.host_socket.socket.accept()
        data = conn.recv(1024)
        conn.close()
        self.assertThat(data, Equals(expected_bytes))

    def test_creates_socket_file(self):
        """
        We assert when we create a lsb we create the session socket
        """
        lsb = LibertineSessionBridge([HostSessionSocketPair(self.host_path, self.session_path)])
        self.assertTrue(os.path.exists(self.session_path))


    def test_data_read_from_host_to_session(self):
        """
        This test shows we are able to proxy data from a host socket to a session client.
        We do this by:
        1) Create a valid host socket
        2) Start a thread which waits to asserts out host socket recv the expected data
        3) Start the lsb thread to create a proxy session socket
        4) We create a fake session client (socket) and connect to the session path
        5) We send the expected bytes to the fake session client socket
        6) We join on the host sock loop, if we never get the expected bytes in the host socket loop we fail
        7) Clean up, and assert all our threads are not alive and have been cleaned up
        """
        expected_bytes = b'Five exclamation marks, the sure sign of an insane mind.'
        host_sock_loop = threading.Thread(target=self.host_read, args=(expected_bytes,))
        host_sock_loop.start()

        lsb = LibertineSessionBridge([HostSessionSocketPair(self.host_path, self.session_path)])
        lsb_process = Process(target=lsb.main_loop)
        lsb_process.start()

        fake_session_client = socket(AF_UNIX, SOCK_STREAM)
        fake_session_client.connect(self.session_path)
        fake_session_client.sendall(expected_bytes)

        host_sock_loop.join(timeout=1)
        fake_session_client.close()
        lsb_process.terminate()
        lsb_process.join(timeout=1)

        self.assertFalse(host_sock_loop.is_alive())
        self.assertFalse(lsb_process.is_alive())
