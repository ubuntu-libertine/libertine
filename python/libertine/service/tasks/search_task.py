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


class SearchTask(BaseTask):
    def __init__(self, container_id, cache, query, monitor, callback):
        super().__init__(lock=None, container_id=container_id, config=None, monitor=monitor, callback=callback)
        self._cache = cache
        self._query = query

    def _run(self):
        self._data(str(self._cache.search(self._query)))
