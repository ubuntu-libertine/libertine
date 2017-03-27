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


class ListTask(BaseTask):
    def __init__(self, config, monitor, callback):
        super().__init__(lock=None, container_id=None, config=config, monitor=monitor, callback=callback)

    def _run(self):
        self._data(json.dumps(self._config.get_containers()))
        self._finished()
