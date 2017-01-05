#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (C) 2016 Canonical Ltd.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import signal

from gi.repository import GLib
from libertine import utils


class ContainerLifecycleServiceRunner(object):
    def __init__(self, service):
        self._service = service

    def _sigterm(self, sig):
        utils.get_logger().warning("Received SIGTERM")
        self._shutdown()

    def _shutdown(self):
        utils.get_logger().info("Shutting down")
        GLib.MainLoop().quit()

    def run(self):
        GLib.unix_signal_add(GLib.PRIORITY_HIGH,
                             signal.SIGTERM,
                             self._sigterm,
                             None)

        try:
            utils.get_logger().info("Starting main loop")
            GLib.MainLoop().run()
        except KeyboardInterrupt:
            self._shutdown()
