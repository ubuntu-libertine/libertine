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

import apt
import re

from libertine import utils
from os import path
from threading import Lock


class AptCache(object):
    """
    Class to find app information using apt-cache
    """
    def __init__(self, container_id):
        super(AptCache, self).__init__()
        self._container = container_id
        self._cache = None
        self._lock = Lock()

    def search(self, query):
        self._load()

        pkg_keys = [key for key in self._cache.keys() if re.match(query, key)]
        apps = []
        for key in pkg_keys:
            apps.append(self._app_to_dict(key))
        return apps

    def app_info(self, app_id):
        self._load()
        return self._app_to_dict(app_id)

    def _app_to_dict(self, app_id):
        app_data = {}
        if app_id in self._cache.keys():
            app = self._cache[app_id]
            app_data["name"] = app.name
            app_data["id"] = app.name
            app_data["package"] = app.name
            if len(app.versions) > 0:
                app_data["summary"] = app.versions[0].summary
                app_data["website"] = app.versions[0].homepage
                app_data["description"] = app.versions[0].description
            app_data["package"] = app.name

        return app_data

    def _load(self):
        with self._lock:
            if self._cache is None:
                try:
                    utils.get_logger().debug("Trying aptcache for container %s" % self._container)
                    container_path = utils.get_libertine_container_rootfs_path(self._container)
                    if not container_path or not path.exists(container_path):
                        raise PermissionError

                    self._cache = apt.Cache(rootdir=container_path)
                except PermissionError:
                    utils.get_logger().debug("Trying system aptcache")
                    self._cache = apt.Cache()
