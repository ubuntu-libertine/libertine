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

import libertine.service.progress
import threading
from abc import ABCMeta, abstractmethod


class BaseTask(metaclass=ABCMeta):
    """
    Abstract class for performing long-running, synchronous operations on a
    Libertine container. Child classes must implement _run, which will execute
    in a separate thread. Override _before to implement pre-execution actions
    without locking; if _before returns False, _run will not be executed.
    """
    def __init__(self, lock, container_id, config, connection, callback):
        self._lock = lock
        self._container = container_id
        self._config = config
        self._callback = callback
        self._connection = connection
        self._progress = None
        self._instant_callback = False

    def matches(self, container, klass):
        return self._container == container and self.__class__ == klass

    @property
    def id(self):
        if self._progress is not None:
            return self._progress.id
        else:
            return None

    @property
    def container(self):
        return self._container or ''

    @property
    def package(self):
        return ''

    @property
    def running(self):
        return not self._progress.done

    def _delayed_callback(self):
        if self._instant_callback:
            self._callback(self)
        else:
            threading.Timer(10, lambda: self._callback(self)).start()

    def start(self):
        self._progress = libertine.service.progress.Progress(self._connection)
        thread = threading.Thread(target=self.run)
        thread.start()
        return thread

    def run(self):
        if not self._before():
            self._progress.finished(self.container)
            self._delayed_callback()
            return

        if self._lock is not None:
            with self._lock:
                self._run()
        else:
            self._run()

        if self.running:
            self._progress.finished(self.container)

        self._delayed_callback()

    @abstractmethod
    def _run(self):
        pass

    def _before(self):
        return True
