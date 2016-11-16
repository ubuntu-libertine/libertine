# Copyright 2016 Canonical Ltd.
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


from .base_task import BaseTask
from libertine import LibertineContainer, utils


class DestroyTask(BaseTask):
    def __init__(self, container_id, config, lock, connection, callback):
        super().__init__(lock=lock, container_id=container_id, config=config, connection=connection, callback=callback)

    def _run(self):
        utils.get_logger().debug("Destroying container '%s'" % self._container)

        container = LibertineContainer(self._container, self._config)
        if not container.destroy_libertine_container():
            self._progress.error("Destroying container '%s' failed" % self._container)
            self._config.update_container_install_status(self._container, "ready")
            return

        self._config.delete_container(self._container)

    def _before(self):
        utils.get_logger().debug("CreateTask::_before")
        if self._config._get_value_by_key(self._container, 'installStatus') != 'ready':
            self._progress.error("Container '%s' does not exist" % self._container)
            return False

        self._config.update_container_install_status(self._container, 'removing')
        return True
