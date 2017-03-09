# Copyright 2017 Canonical Ltd.
#
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


import dbus.service
import threading

from . import constants
from libertine import utils
from time import time


class Download(dbus.service.Object):
    def __init__(self, connection, id):
        self._finished = False
        self._result = ''
        self._error = ''
        dbus.service.Object.__init__(self, conn=connection, object_path=(constants.DOWNLOAD_OBJECT % id))

        # Disabled until something requires the Download interface
        # self.emit_processing()

    # This is currently how services using the Ubuntu SDK to show progress
    # determine whether or not an operation is running.
    def emit_processing(self):
        if not self.done:
            self.processing(self.id)
            threading.Timer(0.5, self.emit_processing).start()

    @property
    def id(self):
        return self._object_path

    @property
    def done(self):
        return self._finished

    @property
    def result(self):
        return self._result.strip()

    @property
    def last_error(self):
        return self._error

    def data(self, message):
        self._result += message + '\n'

    # Signals to satisfy the download interface

    @dbus.service.signal(constants.DOWNLOAD_INTERFACE, signature='o')
    def processing(self, path):
        utils.get_logger().debug("emit processing('%s')" % path)

    @dbus.service.signal(constants.DOWNLOAD_INTERFACE, signature='o')
    def finished(self, path):
        utils.get_logger().debug("emit finished('%s')" % path)
        self._finished = True

    @dbus.service.signal(constants.DOWNLOAD_INTERFACE)
    def progress(self, received, total):
        utils.get_logger().debug("emit progress(%d, %d)" % (received, total))

    @dbus.service.signal(constants.DOWNLOAD_INTERFACE, signature='s')
    def error(self, message):
        utils.get_logger().error("emit error(%s)" % message)
        self._error = message
        self._finished = True
