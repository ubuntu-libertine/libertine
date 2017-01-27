# Copyright 2016-2017 Canonical Ltd.
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
from libertine import utils
from time import time

DOWNLOAD_INTERFACE = "com.canonical.applications.Download"
PROGRESS_INTERFACE = "com.canonical.libertine.Service.Progress"

class Progress(dbus.service.Object):
    def __init__(self, connection):
        utils.get_logger().debug("creating a Progress object")
        self._finished = False
        self._result = []
        self._error = ''
        dbus.service.Object.__init__(self, conn=connection, object_path=("/Progress/%s" % hex(int(time()*10000000))[2:]))

        # self.emit_processing() # Disabled until something requires the Download interface

    @property
    def id(self):
        return self._object_path

    def emit_processing(self):
        if not self.done:
            self.processing(self.id)
            threading.Timer(0.5, self.emit_processing).start()

    @property
    def done(self):
        return self._finished

    @dbus.service.signal(DOWNLOAD_INTERFACE)
    def processing(self, path):
        utils.get_logger().debug("emit processing('%s')" % path)

    @dbus.service.signal(DOWNLOAD_INTERFACE)
    def finished(self, path):
        utils.get_logger().debug("emit finished('%s')" % path)
        self._finished = True

    @dbus.service.signal(DOWNLOAD_INTERFACE)
    def progress(self, received, total):
        utils.get_logger().debug("emit progress(%d, %d)" % (received, total))

    @dbus.service.signal(DOWNLOAD_INTERFACE)
    def error(self, message):
        utils.get_logger().error("emit error(%s)" % message)
        self._error = message
        self._finished = True

    @dbus.service.signal(PROGRESS_INTERFACE)
    def data(self, message):
        utils.get_logger().debug("emit data(%s)" % message)
        self._result.append(message)

    @dbus.service.method(PROGRESS_INTERFACE, out_signature='b')
    def running(self):
        utils.get_logger().debug(not self.done)
        return not self.done

    @dbus.service.method(PROGRESS_INTERFACE, out_signature='s')
    def result(self):
        full_result = "\n".join(self._result)
        utils.get_logger().debug(full_result)
        return full_result

    @dbus.service.method(PROGRESS_INTERFACE, out_signature='s')
    def last_error(self):
        utils.get_logger().debug(self._error)
        return self._error
