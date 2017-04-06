# Copyright 2017 Canonical Ltd.
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
import psutil

from collections import Counter
from libertine import utils


class ContainerControlClient(object):
    def __init__(self):
        self._get_running_apps_per_container()

    def _get_running_apps_per_container(self):
        self._invalid_apps = dict()
        self._operations = Counter()
        config = libertine.ContainersConfig.ContainersConfig()

        for container in config.get_containers():
            running_apps = config.get_running_apps(container).copy()

            for app in running_apps:
                try:
                    proc = psutil.Process(app['pid'])
                    if app['appExecName'] in proc.cmdline():
                        self._operations[container] += 1
                    else:
                        raise
                except:
                    utils.get_logger().error(utils._("Container app '{application_name}' is not valid.").format(application_name=app['appExecName']))
                    if container not in self._invalid_apps:
                        self._invalid_apps[container] = [{app['appExecName'], app['pid']}]
                    else:
                        self._invalid_apps[container].append({app['appExecName'], app['pid']})
                    config.delete_running_app(container, app)
                    continue

    def container_operation_start(self, container):
        if self._operations[container] == -1:
            return False

        self._operations[container] += 1

        return True

    def container_operation_finished(self, container, app_name, pid):
        if container in self._invalid_apps and {app_name, pid} in self._invalid_apps[container]:
            self._invalid_apps[container].remove({app_name, pid})
            if not self._invalid_apps[container]:
                del self._invalid_apps[container]
        else:
            self._operations[container] -= 1

        if self._operations[container] == 0:
            self._operations[container] = -1
            return True

        return False

    def container_stopped(self, container):
        del self._operations[container]
        return True
