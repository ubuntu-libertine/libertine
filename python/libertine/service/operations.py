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


import dbus
import dbus.service

from . import constants, operations_monitor, task_dispatcher
from libertine import utils


class Operations(dbus.service.Object):
    def __init__(self, bus_name, client):
        super().__init__(bus_name, constants.OPERATIONS_OBJECT)

        self._dispatcher = task_dispatcher.TaskDispatcher(operations_monitor.OperationsMonitor(self.connection), client)

    # Information

    @dbus.service.method(constants.OPERATIONS_INTERFACE,
                         in_signature='ss',
                         out_signature='o')
    def search(self, container_id, search_string):
        utils.get_logger().debug("search('{}', '{}') called".format(container_id, search_string))
        return self._dispatcher.search(container_id, search_string)

    @dbus.service.method(constants.OPERATIONS_INTERFACE,
                         in_signature='ss',
                         out_signature='o')
    def app_info(self, container_id, app_id):
        utils.get_logger().debug("app_info('{}', '{}') called".format(container_id, app_id))
        return self._dispatcher.app_info(container_id, app_id)

    @dbus.service.method(constants.OPERATIONS_INTERFACE,
                         in_signature='s',
                         out_signature='o')
    def container_info(self, container_id):
        utils.get_logger().debug("container_info('{}')".format(container_id))
        return self._dispatcher.container_info(container_id)

    @dbus.service.method(constants.OPERATIONS_INTERFACE,
                         in_signature='s',
                         out_signature='o')
    def list_app_ids(self, container_id):
        utils.get_logger().debug("list_app_ids('{}')".format(container_id))
        return self._dispatcher.list_app_ids(container_id)

    @dbus.service.method(constants.OPERATIONS_INTERFACE,
                         out_signature='o')
    def list(self):
        utils.get_logger().debug("list()")
        return self._dispatcher.list()

    # Operations

    @dbus.service.method(constants.OPERATIONS_INTERFACE,
                         in_signature='ssssb',
                         out_signature='o')
    def create(self, container_id, container_name='', distro='', container_type='', enable_multiarch=False):
        utils.get_logger().debug("create('{}', '{}', '{}', '{}', '{}')".format(container_id, container_name, distro, container_type, enable_multiarch))
        return self._dispatcher.create(container_id, container_name, distro, container_type, enable_multiarch)

    @dbus.service.method(constants.OPERATIONS_INTERFACE,
                         in_signature='s',
                         out_signature='o')
    def destroy(self, container_id):
        utils.get_logger().debug("destroy('{}')".format(container_id))
        return self._dispatcher.destroy(container_id)

    @dbus.service.method(constants.OPERATIONS_INTERFACE,
                         in_signature='s',
                         out_signature='o')
    def update(self, container_id):
        utils.get_logger().debug("update('{}')".format(container_id))
        return self._dispatcher.update(container_id)

    @dbus.service.method(constants.OPERATIONS_INTERFACE,
                         in_signature='ss',
                         out_signature='o')
    def install(self, container_id, package_name):
        utils.get_logger().debug("install('%s', '%s')" % (container_id, package_name))
        return self._dispatcher.install(container_id, package_name)

    @dbus.service.method(constants.OPERATIONS_INTERFACE,
                         in_signature='ss',
                         out_signature='o')
    def remove(self, container_id, package_name):
        utils.get_logger().debug("remove('%s', '%s')" % (container_id, package_name))
        return self._dispatcher.remove(container_id, package_name)
