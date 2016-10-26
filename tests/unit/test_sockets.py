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

from libertine import Socket

from socket import socket

from testtools import TestCase
from testtools.matchers import Equals, NotEquals

class FakeSocket(Socket):
    """
    We are making things up here... soo lets not attempt to remove anything!
    """
    def __del__(self):
        pass


class TestSocket(TestCase):
    def setUp(self):
        super(TestSocket, self).setUp()
        self.socket1 = socket()
        self.socket2 = socket()

    """
    Test we can wrap a python socket.socket in our Socket class
    """
    def test_socket_warp(self):
        s = FakeSocket(self.socket1)
        self.assertThat(s, Equals(self.socket1))

    """
    Test our equivalence operator works on three types:
        1: Other Socket classes
        2: Python socket classes
        3: The fd/socket raw Int value
    """
    def test_socket_eq_op(self):
        s1 = FakeSocket(self.socket1)
        s2 = FakeSocket(self.socket1)
        self.assertThat(s1, Equals(s2))
        self.assertThat(s2, Equals(self.socket1))
        self.assertThat(s2, Equals(self.socket1.fileno()))

    """
    Test our not equivalence works on the same three types
    """
    def test_socket_not_eq_op(self):
        s1 = FakeSocket(self.socket1)
        s2 = FakeSocket(self.socket2)
        self.assertThat(s1, NotEquals(s2))
        self.assertThat(s2, NotEquals(self.socket1))
        self.assertThat(s2, NotEquals(self.socket1.fileno()))

    """
    Test our Socket wrapper class is also hashable
    """
    def test_socket_is_hashable(self):
        s   = FakeSocket(self.socket1)
        dic = {s: 17}
        self.assertThat(dic[s], Equals(17))
