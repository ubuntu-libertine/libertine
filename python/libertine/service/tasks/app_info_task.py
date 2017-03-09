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


from .base_task import BaseTask
from libertine import utils


class AppInfoTask(BaseTask):
    def __init__(self, container_id, cache, app_id, tasks, config, monitor, callback):
        super().__init__(lock=None, container_id=container_id, config=config, monitor=monitor, callback=callback)
        self._cache = cache
        self._app_id = app_id
        self._tasks = tasks

    def _run(self):
        app = self._cache.app_info(self._app_id)
        if app == {}:
            self._error("Could not find app info for '%s' in container '%s'" % (self._app_id, self._container))
            return

        app['status'] = self._config.get_package_install_status(self._container, app['package']) or ''
        app['task_ids'] = self._tasks
        self._data(str(app))
