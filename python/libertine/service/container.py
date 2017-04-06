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

from libertine.service.tasks import *
from libertine import utils
from threading import Lock

if not utils.is_snap_environment():
    from libertine.service import apt


class Container(object):
    def __init__(self, container_id, config, monitor, client, callback):
        self._id = container_id
        self._config = config
        self._monitor = monitor
        self._client = client
        self._callback = callback

        self._lock = Lock()
        self._tasks = []

        if utils.is_snap_environment():
            utils.get_logger().warning(utils._("Using AptCache not currently supported in snap environment"))
            self._cache = None
        else:
            self._cache = apt.AptCache(self.id)

    def _cleanup_task(self, task):
        utils.get_logger().debug("cleaning up tasks for container '%s'" % self.id)

        if task in self._tasks:
            self._tasks.remove(task)

        if len(self._tasks) == 0:
            self._callback(self)

    @property
    def id(self):
        return self._id

    @property
    def tasks(self):
        return [task.id for task in self._tasks if task.running]

    def install(self, package_name):
        utils.get_logger().debug("Install package '%s' from container '%s'" % (package_name, self.id))

        tasks = [t for t in self._tasks if t.matches(package_name, InstallTask) and t.running]
        if len(tasks) > 0:
            utils.get_logger().debug("Install already in progress for '%s':'%s'" % (package_name, self.id))
            return tasks[0].id

        task = InstallTask(package_name, self.id, self._config, self._lock, self._monitor, self._client, self._cleanup_task)
        self._tasks.append(task)
        task.start()
        return task.id

    def remove(self, package_name):
        utils.get_logger().debug("Remove package '%s' from container '%s'" % (package_name, self.id))

        tasks = [t for t in self._tasks if t.matches(package_name, RemoveTask) and t.running]
        if len(tasks) > 0:
            utils.get_logger().debug("Remove already in progress for '%s':'%s'" % (package_name, self.id))
            return tasks[0].id

        task = RemoveTask(package_name, self.id, self._config, self._lock, self._monitor, self._client, self._cleanup_task)
        self._tasks.append(task)
        task.start()
        return task.id

    def create(self, container_name, distro, container_type, enable_multiarch):
        utils.get_logger().debug("Create container with ID '%s'" % self.id)

        tasks = [t for t in self._tasks if t.matches(self.id, CreateTask) and t.running]
        if len(tasks) > 0:
            utils.get_logger().debug("Create already in progress for '%s'" % self.id)
            return tasks[0].id

        task = CreateTask(self.id, container_name, distro, container_type, enable_multiarch,
                          self._config, self._lock, self._monitor, self._client, self._cleanup_task)
        self._tasks.append(task)
        task.start()
        return task.id

    def destroy(self):
        utils.get_logger().debug("Destroy container with ID '%s'" % self.id)

        tasks = [t for t in self._tasks if t.matches(self.id, DestroyTask) and t.running]
        if len(tasks) > 0:
            utils.get_logger().debug("Destroy already in progress for '%s'" % self.id)
            return tasks[0].id

        task = DestroyTask(self.id, self._config, self._lock, self._monitor, self._client, self._cleanup_task)
        self._tasks.append(task)
        task.start()
        return task.id

    def update(self):
        utils.get_logger().debug("Update container with ID '%s'" % self.id)

        tasks = [t for t in self._tasks if t.matches(self.id, UpdateTask) and t.running]
        if len(tasks) > 0:
            utils.get_logger().debug("Update already in progress for '%s'" % self.id)
            return tasks[0].id

        task = UpdateTask(self.id, self._config, self._lock, self._monitor, self._client, self._cleanup_task)
        self._tasks.append(task)
        task.start()
        return task.id

    # Tasks which don't require starting/stopping the container

    def list_app_ids(self):
        utils.get_logger().debug("List all app ids in container '%s'" % self.id)

        task = ListAppIdsTask(self.id, self._config, self._monitor, self._client, self._cleanup_task)

        self._tasks.append(task)
        task.start()
        return task.id

    def search(self, query):
        utils.get_logger().debug("search container '%s' for package '%s'" % (self.id, query))

        if utils.is_snap_environment():
            raise Exception("This operation is not currently supported within the snap")

        task = SearchTask(self.id, self._cache, query, self._monitor, self._cleanup_task)
        self._tasks.append(task)
        task.start()

        return task.id

    def app_info(self, package_name):
        utils.get_logger().debug("get info for package '%s' in container '%s'" % (package_name, self.id))

        if utils.is_snap_environment():
            raise Exception("This operation is not currently supported within the snap")

        related_task_ids = [t.id for t in self._tasks if t.package == package_name and t.running]
        task = AppInfoTask(self.id, self._cache, package_name, related_task_ids, self._config, self._monitor, self._cleanup_task)

        self._tasks.append(task)
        task.start()
        return task.id
