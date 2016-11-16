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


class ListAppsTask(BaseTask):
    def __init__(self, container_id, config, connection, callback):
        super().__init__(lock=None, container_id=container_id, config=config, connection=connection, callback=callback)

    def _run(self):
        utils.get_logger().debug("Listing apps in container '%s'" % self._container)
        if not self._config.container_exists(self._container):
            self._progress.error("Container '%s' does not exist, skipping list" % self._container)
        else:
            container = LibertineContainer(self._container, self._config)
            self._progress.data(str(container.list_app_launchers(use_json=True)))
