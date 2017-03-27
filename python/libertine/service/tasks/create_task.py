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
from libertine.HostInfo import HostInfo


class CreateTask(ContainerBaseTask):
    def __init__(self, container_id, container_name, distro, container_type, enable_multiarch,
                       config, lock, monitor, client, callback):
        super().__init__(lock=lock, container_id=container_id, config=config,
                         monitor=monitor, client=client, callback=callback)
        self._name = container_name
        self._distro = distro
        self._type = container_type
        self._multiarch = enable_multiarch

    def _run(self):
        utils.get_logger().debug("Creating container '%s'" % self._container)

        try:
            container = LibertineContainer(self._container, self._config, self._client)

            if not container.create_libertine_container(password='', multiarch=self._multiarch):
                self._config.delete_container(self._container)
                self._error("Creating container '%s' failed" % self._container)
            else:
                self._config.update_container_install_status(self._container, "ready")
                self._finished()
        except RuntimeError as e:
            self._config.delete_container(self._container)
            self._error(str(e))

    def _before(self):
        utils.get_logger().debug("CreateTask::_before")
        if self._config.container_exists(self._container):
            self._error("Container '%s' already exists" % self._container)
            return False

        info = HostInfo()
        if not self._distro:
            self._distro = info.get_host_distro_release()
        elif not info.is_distro_valid(self._distro):
            self._error("Invalid distro '%s'." % self._distro)
            return False

        if not self._type:
            self._type = info.select_container_type_by_kernel()
        elif (self._type == 'lxd' and not info.has_lxd_support()) or \
             (self._type == 'lxc' and not info.has_lxc_support()):
            self._error("System kernel does not support %s type containers. "
                                 "Please either use chroot or leave empty." % self._type)
            return False

        if not self._name:
            self._name = "Ubuntu \'" + info.get_distro_codename(self._distro) + "\'"

        self._config.add_new_container(self._container, self._name, self._type, self._distro)

        if self._multiarch:
            self._config.update_container_multiarch_support(self._container, 'enabled')

        self._config.update_container_install_status(self._container, 'installing')
        return True
