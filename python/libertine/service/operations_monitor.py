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
import uuid

from . import constants, download
from libertine import utils
from time import time


class OperationsMonitor(dbus.service.Object):
    def __init__(self, connection):
        self._operations = []
        dbus.service.Object.__init__(self, conn=connection, object_path=constants.OPERATIONS_MONITOR_OBJECT)

    def new_operation(self):
        self._operations.append(download.Download(self.connection, str(uuid.uuid4().fields[-1])))
        return self._operations[-1].id

    def remove_from_connection(self, path):
        operation = self._operation(path)
        self._operations.remove(operation)
        operation.remove_from_connection()

    def done(self, path):
        op = self._operation(path)
        if op:
            return op.done
        else:
            return False

    def _operation(self, path):
        operations = [op for op in self._operations if op.id == path]
        if not operations:
            return None

        return operations[0]

    @dbus.service.signal(constants.OPERATIONS_MONITOR_INTERFACE, signature='o')
    def finished(self, path):
        op = self._operation(path)
        if op:
            op.finished(path)

    @dbus.service.signal(constants.OPERATIONS_MONITOR_INTERFACE, signature='os')
    def error(self, path, message):
        op = self._operation(path)
        if op:
            op.error(message)

    @dbus.service.signal(constants.OPERATIONS_MONITOR_INTERFACE, signature='os')
    def data(self, path, message):
        op = self._operation(path)
        if op:
            op.data(message)

    @dbus.service.method(constants.OPERATIONS_MONITOR_INTERFACE, in_signature='o', out_signature='b')
    def running(self, path):
        op = self._operation(path)
        if op:
            return not op.done
        else:
            return False

    @dbus.service.method(constants.OPERATIONS_MONITOR_INTERFACE, in_signature='o', out_signature='s')
    def result(self, path):
        op = self._operation(path)
        if op:
            return op.result
        else:
            return ''

    @dbus.service.method(constants.OPERATIONS_MONITOR_INTERFACE, in_signature='o', out_signature='s')
    def last_error(self, path):
        op = self._operation(path)
        if op:
            return op.last_error
        else:
            return ''
