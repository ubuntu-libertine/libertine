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


import libertine.ContainersConfig
from libertine.service.container import Container
from libertine.service.tasks import *
from libertine import utils


class TaskDispatcher(object):
    def __init__(self, monitor, client):
        self._monitor = monitor
        self._client = client
        self._config = libertine.ContainersConfig.ContainersConfig()
        self._containerless_tasks = []
        self._tasks = []
        self._containers = []

    def _cleanup_task(self, task):
        utils.get_logger().debug("cleaning up containerless task '%s'" % task.id)
        if task in self._tasks:
            self._tasks.remove(task)

    def _cleanup_container(self, container):
        utils.get_logger().debug("cleaning up container '%s'" % container.id)
        if container in self._containers:
            self._containers.remove(container)

    def _find_or_create_container(self, container_id):
        utils.get_logger().debug("finding or creating container '%s'" % container_id)

        container = self._find_container(container_id)
        if container is not None:
            utils.get_logger().debug("using existing container '%s'" % container_id)
            return container

        container = Container(container_id, self._config, self._monitor, self._client, self._cleanup_container)
        self._containers.append(container)

        return container

    def _find_container(self, container_id):
        containers = [c for c in self._containers if c.id == container_id]
        if len(containers) > 0:
            return containers[0]

    # Tasks (usually) run within a container

    def search(self, container_id, query):
        utils.get_logger().debug("dispatching search in container '%s' for package '%s'" % (container_id, query))
        return self._find_or_create_container(container_id).search(query)

    def app_info(self, container_id, app_id):
        utils.get_logger().debug("dispatching app_info in container '%s' for package '%s'" % (container_id, app_id))
        return self._find_or_create_container(container_id).app_info(app_id)

    def install(self, container_id, package_name):
        utils.get_logger().debug("dispatching install of package '%s' from container '%s'" % (package_name, container_id))
        return self._find_or_create_container(container_id).install(package_name)

    def remove(self, container_id, package_name):
        utils.get_logger().debug("dispatching remove of package '%s' from container '%s'" % (package_name, container_id))
        return self._find_or_create_container(container_id).remove(package_name)

    def create(self, container_id, container_name, distro, container_type, enable_multiarch):
        utils.get_logger().debug("dispatching create of container '%s'" % container_id)
        return self._find_or_create_container(container_id).create(container_name, distro, container_type, enable_multiarch)

    def destroy(self, container_id):
        utils.get_logger().debug("dispatching destroy container '%s'" % container_id)
        return self._find_or_create_container(container_id).destroy()

    def update(self, container_id):
        utils.get_logger().debug("dispatching update container '%s'" % container_id)
        return self._find_or_create_container(container_id).update()

    def list_app_ids(self, container_id):
        utils.get_logger().debug("dispatching list apps ids in container '%s'" % container_id)
        return self._find_or_create_container(container_id).list_app_ids()

    # Containerless Tasks

    def container_info(self, container_id):
        utils.get_logger().debug("dispatching get info for container '%s'" % container_id)

        related_task_ids = []
        container = self._find_container(container_id)
        if container is not None:
            related_task_ids = container.tasks
        task = ContainerInfoTask(container_id, related_task_ids, self._config, self._monitor, self._cleanup_task)
        self._tasks.append(task)
        task.start()

        return task.id

    def list(self):
        utils.get_logger().debug("dispatching list all containers")

        task = ListTask(self._config, self._monitor, self._cleanup_task)
        self._tasks.append(task)
        task.start()

        return task.id
