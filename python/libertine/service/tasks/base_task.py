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


import threading

from abc import ABCMeta, abstractmethod


class BaseTask(metaclass=ABCMeta):
    """
    Abstract class for performing long-running, synchronous operations on a
    Libertine container. Child classes must implement _run, which will execute
    in a separate thread. Override _before to implement pre-execution actions
    without locking; if _before returns False, _run will not be executed.
    """
    def __init__(self, lock, container_id, config, monitor, callback):
        self._lock = lock
        self._container = container_id
        self._config = config
        self._callback = callback
        self._monitor = monitor
        self._operation_id = None
        self._instant_callback = False # for testing

    def matches(self, container, klass):
        return self._container == container and self.__class__ == klass

    @property
    def id(self):
        return self._operation_id

    @property
    def container(self):
        return self._container or ''

    @property
    def package(self):
        return ''

    @property
    def running(self):
        return not self._monitor.done(self._operation_id)

    def _delayed_callback(self):
        if self._instant_callback:
            self._callback(self)
        else:
            threading.Timer(10, lambda: (self._monitor.remove_from_connection(self._operation_id), self._callback(self))).start()

    def start(self):
        self._operation_id = self._monitor.new_operation()
        thread = threading.Thread(target=self.run)
        thread.start()
        return thread

    def run(self):
        self._refresh_database()

        if not self._before():
            self._monitor.finished(self._operation_id)
            self._delayed_callback()
            return

        if self._lock is not None:
            with self._lock:
                self._refresh_database(False)
                self._run()
        else:
            self._refresh_database()
            self._run()

        if self.running:
            self._finished()

        self._delayed_callback()

    def _refresh_database(self, require_lock=True):
        if self._config:
            if require_lock and self._lock is not None:
                with self._lock:
                    self._config.refresh_database()
            else:
                self._config.refresh_database()

    @abstractmethod
    def _run(self):
        pass

    def _before(self):
        return True

    def _data(self, message):
        self._monitor.data(self._operation_id, message)

    def _finished(self):
        self._monitor.finished(self._operation_id)

    def _error(self, message):
        self._monitor.error(self._operation_id, message)


class ContainerBaseTask(BaseTask):
    def __init__(self, lock, container_id, config, monitor, client, callback):
        super().__init__(lock=lock, container_id=container_id, config=config, monitor=monitor, callback=callback)
        self._client = client
