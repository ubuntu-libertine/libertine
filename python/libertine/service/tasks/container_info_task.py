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
from libertine import utils


class ContainerInfoTask(BaseTask):
    def __init__(self, container_id, tasks, config, connection, callback):
        super().__init__(lock=None, container_id=container_id, config=config, connection=connection, callback=callback)
        self._tasks = tasks

    def _run(self):
        container = {'id': str(self._container)}
        container['status'] = self._config._get_value_by_key(self._container, 'installStatus') or ''
        container['task_ids'] = self._tasks
        self._progress.data(str(container))
