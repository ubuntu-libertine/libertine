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


from .base_task import ContainerBaseTask
from libertine import LibertineContainer, utils


class RemoveTask(ContainerBaseTask):
    def __init__(self, package_name, container_id, config, lock, monitor, client, callback):
        super().__init__(lock=lock, container_id=container_id, config=config, monitor=monitor, client=client, callback=callback)
        self._package = package_name

    def matches(self, package, klass):
        return self._package == package and self.__class__ == klass

    @property
    def package(self):
        return self._package

    def _run(self):
        utils.get_logger().debug("Removing package '%s'" % self._package)
        container = LibertineContainer(self._container, self._config, self._client)
        if container.remove_package(self._package):
            self._config.delete_package(self._container, self._package)
            self._finished()
        else:
            self._config.update_package_install_status(self._container, self._package, 'installed')
            self._error("Package removal failed for '%s'" % self._package)

    def _before(self):
        utils.get_logger().debug("RemoveTask::_before")
        if self._config.get_package_install_status(self._container, self._package) == 'installed':
            self._config.update_package_install_status(self._container, self._package, "removing")
            return True
        else:
            self._error("Package '%s' not installed, skipping remove" % self._package)
            return False
