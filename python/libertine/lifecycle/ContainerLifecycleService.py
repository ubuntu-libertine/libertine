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


import dbus.exceptions
import dbus.service

from .LifecycleResult import LifecycleResult
from collections import Counter
from dbus.mainloop.glib import DBusGMainLoop
from libertine import utils


LIBERTINE_CONTAINER_LIFECYCLE_INTERFACE = 'com.canonical.libertine.ContainerLifecycle'


class ContainerLifecycleService(dbus.service.Object):
    def __init__(self, service_name, service_path):
        self._apps = Counter()
        self._operations = Counter()

        DBusGMainLoop(set_as_default=True)
        try:
            bus_name = dbus.service.BusName(service_name,
                                            bus=dbus.SessionBus(),
                                            do_not_queue=True)
        except dbus.exceptions.NameExistsException:
            utils.get_logger().error("service is already running")
            raise
        super().__init__(bus_name, service_path)

    def start(self, container):
        raise NotImplementedError("Subclasses must implement start(container)")

    def stop(self, container, options={}):
        raise NotImplementedError("Subclasses must implement stop(container)")

    @dbus.service.method(LIBERTINE_CONTAINER_LIFECYCLE_INTERFACE,
                         in_signature='s',
                         out_signature='a{ss}')
    def app_start(self, container):
        utils.get_logger().debug("app_start({})".format(container))
        if self._operations[container] != 0:
            return LifecycleResult("Libertine container operation already running: cannot launch application.").to_dict()

        result = self.start(container, True)

        if result.success:
            self._apps[container] += 1

        return result.to_dict()

    @dbus.service.method(LIBERTINE_CONTAINER_LIFECYCLE_INTERFACE,
                         in_signature='s',
                         out_signature='a{ss}')
    def app_stop(self, container):
        utils.get_logger().debug("app_stop({})".format(container))
        self._apps[container] -= 1
        result = LifecycleResult()

        if self._apps[container] == 0:
            result = self.stop(container)
            del self._apps[container]

        return result.to_dict()

    @dbus.service.method(LIBERTINE_CONTAINER_LIFECYCLE_INTERFACE,
                         in_signature='s',
                         out_signature='a{ss}')
    def operation_start(self, container):
        utils.get_logger().debug("operation_start({})".format(container))
        if self._apps[container] != 0:
            return LifecycleResult("Application already running in container: cannot run operation.").to_dict()

        result = self.start(container, False)

        if result.success:
            self._operations[container] += 1

        return result.to_dict()

    @dbus.service.method(LIBERTINE_CONTAINER_LIFECYCLE_INTERFACE,
                         in_signature='sa{ss}',
                         out_signature='a{ss}')
    def operation_stop(self, container, options={}):
        utils.get_logger().debug("operation_stop({}, {})".format(container, options))
        self._operations[container] -= 1
        result = LifecycleResult()

        if self._operations[container] == 0:
            result = self.stop(container, options)
            del self._operations[container]

        return result.to_dict()
