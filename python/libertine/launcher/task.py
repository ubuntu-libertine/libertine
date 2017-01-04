# Copyright 2016 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Pre- and post-launch tasks surrounding the Libertine launch of an application."""


from os import waitpid, WNOHANG
from subprocess import Popen


class TaskType:
    """Namespace used for task type enumeration."""

    LAUNCH_SERVICE = 1


class TaskConfig(object):
    """Encapsulation of the configuration of a single launch task."""

    def __init__(self, task_type, datum):
        """
        :param task_type: The type of launch task.
        :tyoe task_type: a TaskType value
        :param datum: The data associated with the launch task.
        :type datum: anything -- usually a collection of data
        """
        self.task_type = task_type
        self.datum = datum


class LaunchServiceTask(object):
    """A task that launches a service."""

    def __init__(self, config):
        """
        :param config: The task configuration.
        :type config: TaskConfig

        The constructor unpacks the service commandline from the config datum.
        """
        self._command_line = config.datum
        self._process = None

    def start(self, environ=None):
        """Start the service.

        :param env: An alternate environment dictionary.
        """
        self._process = Popen(self._command_line, env=environ)

    def stop(self):
        """Shuts the service down."""
        try:
            self._process.terminate()
        except ProcessLookupError:
            pass

    def wait(self):
        """Wait for service shutdown to complete.
        :return: True if the service process was successfully waited for, False
                 otherwise (which implies the service is still running).
        """
        (pid, status) = waitpid(self._process.pid, WNOHANG)
        return pid == self._process.pid
