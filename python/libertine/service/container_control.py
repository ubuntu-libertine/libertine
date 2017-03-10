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


import dbus

from . import constants
from libertine import utils


class ContainerControl(dbus.service.Object):
    def __init__(self, connection, client):
        dbus.service.Object.__init__(self, conn=connection, object_path=constants.CONTAINER_CONTROL_OBJECT)
        self._client = client

    @dbus.service.method(constants.CONTAINER_CONTROL_INTERFACE,
                         in_signature='s',
                         out_signature='b')
    def start(self, container):
        utils.get_logger().debug("start({})".format(container))
        return self._client.container_operation_start(container)

    @dbus.service.method(constants.CONTAINER_CONTROL_INTERFACE,
                         in_signature='ssi',
                         out_signature='b')
    def finished(self, container, app_name, pid):
        utils.get_logger().debug("finished({})".format(container))
        return self._client.container_operation_finished(container, app_name, pid)

    @dbus.service.method(constants.CONTAINER_CONTROL_INTERFACE,
                         in_signature='s',
                         out_signature='b')
    def stopped(self, container):
        utils.get_logger().debug("stopped({})".format(container))
        return self._client.container_stopped(container)
