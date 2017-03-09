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


import json

from .base_task import BaseTask
from libertine import utils


class ContainerInfoTask(BaseTask):
    def __init__(self, container_id, tasks, config, monitor, callback):
        super().__init__(lock=None, container_id=container_id, config=config, monitor=monitor, callback=callback)
        self._tasks = tasks

    def _run(self):
        utils.get_logger().debug("Gathering info for container '{}'".format(self._container))
        container = {'id': str(self._container), 'task_ids': self._tasks}

        container['status'] = self._config.get_container_install_status(self._container) or ''
        container['name'] = self._config.get_container_name(self._container) or ''

        container_type = self._config.get_container_type(self._container)
        container['root'] = utils.get_libertine_container_rootfs_path(self._container)
        container['home'] = utils.get_libertine_container_home_dir(self._container)

        self._data(json.dumps(container))

    def _before(self):
        if not self._config.container_exists(self._container):
            self._error("Container '%s' does not exist, ignoring info request" % self._container)
            return False

        return True
