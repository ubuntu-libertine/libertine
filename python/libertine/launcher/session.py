# Copyright 2016-2017 Canonical Ltd.
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

"""High-level interface for starting and running an application in Libertine."""

import os
import selectors
import signal
import struct
import sys

from .config import Config
from .. import utils
from contextlib import ExitStack, suppress
from libertine.ContainersConfig import ContainersConfig
from psutil import STATUS_ZOMBIE
from socket import socket, AF_UNIX, SOCK_STREAM, SHUT_RDWR
from .task import LaunchServiceTask, TaskType


def translate_to_real_address(abstract_address):
    """Translate the notional text address to a real UNIX-domain address string.

    :param abstract_address: The human-readable abstract socket address string.

    Trims off any suffix starting with a comma and replaces any leading string of
    'unix:abstract=' with a zero byte.
    """
    addr = abstract_address.split(',')[0]
    if addr.startswith('unix:abstract='):
        return "\0" + ' '.join(addr.split('=')[1:])
    elif addr.startswith('unix:path='):
        return ' '.join(addr.split('=')[1:])

    return addr


class BridgePair(object):
    """A pair of sockets that make up a bridge between host and session."""

    def __init__(self, session_socket, host_address):
        """Create a pair of sockets bridging host and session.

        A socket bridge pair takes an (already-opened) session socket and the
        address of the host socket and opens a connection to that.
        """
        self.session_socket = session_socket
        self.session_socket.setblocking(False)

        self.host_socket = socket(AF_UNIX, SOCK_STREAM)
        self.host_socket.connect(translate_to_real_address(host_address))
        self.host_socket.setblocking(False)

    def handle_read_fd(self, fd, session):
        """Handle read-available events on one of the sockets.

        :param fd: A file descriptor on which a read is available.
        :type fd: int -- valid file descriptor.
        :param session: A libertine application session object.
        :type session: libertine.launcher.Session

        Callback to handle a read-available event on one of the bridge pair
        socket fds.
        """
        if fd == self.session_socket.fileno():
            if self._copy_data(self.session_socket, self.host_socket) == 0:
                self._close_up_shop(session)
        elif fd == self.host_socket.fileno():
            if self._copy_data(self.host_socket, self.session_socket) == 0:
                self._close_up_shop(session)

    def _copy_data(self, from_socket, to_socket):
        """Copy data between the sockets.

        :param from_socket: A socket to be read from.
        :type from_socket: socket-object
        :param to_socket: A socket to be written to.
        :type to_socket: socket-object

        Note that this chunks the data 4 kilobytes at a time (which maybe should
        be a tuneable parameter).
        Also, it's a non-blocking write and that may affect things.  Honestly, it
        should be a non-blocking write and logic should be added to track
        write-available events and unsent bytes and all that stuff but not today.
        """
        try:
            b = from_socket.recv(4096)
            if len(b) > 0:
                to_socket.sendall(b)
                utils.get_logger().debug('copied {} bytes from fd to {}'.format(len(b), from_socket, to_socket))
            else:
                utils.get_logger().info(utils._('close detected on {socket}').format(socket=from_socket))
            return len(b)
        except Exception as e:
            utils.get_logger().debug(e)
            return 0

    def _close_up_shop(self, session):
        """Clean up.

        :param session: A libertine application session object.
        :type session: libertine.launcher.Session

        Closes both sockets in the pair and calls back the session to remove
        this object from its watch list.
        """
        session.remove_bridge_pair(self)
        self.session_socket.shutdown(SHUT_RDWR)
        self.session_socket.close()

        self.host_socket.shutdown(SHUT_RDWR)
        self.host_socket.close()


class Session(ExitStack):
    """Encapsulation of a running application under a Libertine aegis.

    A session includes the following.

    * A cleansed and remapped set of environment variables.
    * A collection of redirected sockets.
    * Zero or more running auxiliary programs.
    * An executable command line.

    A session must be associated with a single aegis (a container, a snap, or
    the host itself, depending).  The associated aegis is termed the *container*
    for historical reasons.

    Each application run under a Libertine aegis must have its own session.

    A session is constructed in a 'stopped' state.  It needs to be started and
    the main loop entered, and once the main loop exits it gets torn down and
    returned to a stopped state.
    """

    def __init__(self, config, container):
        """Construct a libertine application session for a container.

        :param config:    A session configuration object.
        :param container: The container in which the application will be run.
        """
        super().__init__()
        self._app = None
        self._config = config
        self._container = container
        self._bridge_pairs = []
        self._child_processes = []
        self._selector = selectors.DefaultSelector()
        self._set_signal_handlers()
        self.callback(self._shutdown)

        self._ensure_paths_exist()

        with suppress(AttributeError):
            for bridge_config in self._config.socket_bridges:
                self._create_bridge_listener(bridge_config)

        with suppress(AttributeError):
            for task_config in self._config.prelaunch_tasks:
                if task_config.task_type == TaskType.LAUNCH_SERVICE:
                    utils.get_logger().info(utils._("launching {launch_task}").format(launch_task=task_config.datum[0]))
                    task = LaunchServiceTask(task_config)
                    self._child_processes.append(task)
                    task.start(self._config.host_environ)

    @property
    def id(self):
        """A unique string identifying this session."""
        return self._config.id

    def _add_read_fd_handler(self, fd, handler, datum):
        """Add a handler to be called when a read event is received on fd.

        :param fd: A file descriptor to watch for read events.
        :type fd: int -- valid file descriptor.
        :param handler: A function to be called when a read on fd becomes available.
        :param datum: Data to be passed to handler when called.
        """
        self._selector.register(fd, selectors.EVENT_READ, (handler, datum))

    def _remove_read_fd_handler(self, fd):
        """Remove a handler used for reading events on an fd.

        :param fd: A file descriptor to be removed from watching read events.
        """
        self._selector.unregister(fd)

    def add_bridge_pair(self, bridge_pair):
        """Add a bridge pair to the list of those being monitored.

        :param bridge_pair: an active BridgePair object to add to the watch list.
        """
        self._add_read_fd_handler(bridge_pair.session_socket.fileno(),
                                  bridge_pair.handle_read_fd,
                                  self)
        self._add_read_fd_handler(bridge_pair.host_socket.fileno(),
                                  bridge_pair.handle_read_fd,
                                  self)
        self._bridge_pairs.append(bridge_pair)

    def remove_bridge_pair(self, bridge_pair):
        """Remove a bridge pair from the list of those being monitored.

        :param bridge_pair: an active BridgePair object to remove from the watch list.
        """
        self._remove_read_fd_handler(bridge_pair.session_socket.fileno())
        self._remove_read_fd_handler(bridge_pair.host_socket.fileno())
        self._bridge_pairs.remove(bridge_pair)

    def run(self):
        """Run the main event loop of the Session.

        The main loop monitors the various socket bridges and the contained
        child process(es) and dispatches events appropriately.

        The event loop is generally terminated by the receipt of a StopIteration
        exception.
        """
        with suppress(StopIteration):
            while True:
                events = self._selector.select()
                for key, mask in events:
                    handler, datum = key.data
                    handler(key.fd, datum)

        self._container.finish_application(self._app)

        if self._config.container_id:
            self._remove_running_app()

        self._stop_services()

    def start_application(self):
        """Connect to the container and start the application running."""
        self._container.connect()
        self.callback(self._container.disconnect)
        self._app = self._container.start_application(self._config.exec_line,
                                                      self._config.session_environ)
        if self._app:
            self._add_running_app()
        else:
            self._stop_services()

        return self._app != None

    def _add_running_app(self):
        """Add a running app entry to ContainersConfig.json."""
        if self._config.container_id:
            ContainersConfig().add_running_app(self._config.container_id, self._config.exec_line[0], self._app.pid)

    def _remove_running_app(self):
        """Remove a running app entry from ContainersConfig.json."""
        if self._config.container_id:
            containers_config = ContainersConfig()
            running_app = containers_config.find_running_app_by_name_and_pid(self._config.container_id,
                                                                             self._config.exec_line[0],
                                                                             self._app.pid)

            if running_app:
                containers_config.delete_running_app(self._config.container_id, running_app)

    def _create_bridge_listener(self, bridge_config):
        """Create a socket bridge listener for a socket bridge configuration.

        :param bridge_config: A socket bridge configuration object.
        :type bridge_config: libertine.launcher.config.SocketBridge

        The purpose of the listener is to listen on the session socket and
        create a socket bridge to the host when a connection from the session is
        made.
        """
        utils.get_logger().debug('creating bridge listener for {} on {}'.
                  format(bridge_config.env_var, bridge_config.session_address))
        sock = socket(AF_UNIX, SOCK_STREAM)
        sock.bind(translate_to_real_address(bridge_config.session_address))
        sock.listen(5)
        self._add_read_fd_handler(sock.fileno(),
                                  self._accept_bridge_connection,
                                  (bridge_config, sock))

    def _accept_bridge_connection(self, fd, datum):
        """Handle a connection on a session socket.

        :param fd: A file descriptor with an active connect operation in
                   progress.
        :type fd: int -- valid file descriptor.
        :param datum: Data passed to handler.
        """
        (bridge_config, sock) = datum
        conn = sock.accept()
        utils.get_logger().debug('connection of session socket {} accepted'.format(bridge_config.session_address))
        self.add_bridge_pair(BridgePair(conn[0], bridge_config.host_address))

    def _ensure_paths_exist(self):
        """Ensure the required paths all exist for supporting the session."""
        directory = utils.get_libertine_runtime_dir()
        if not os.path.exists(directory):
            os.makedirs(directory)

    def _handle_child_died(self):
        """Take action when a SIGCHILD has been raised."""
        for child in self._child_processes:
            if child.wait():
                return True

        if self._app == None or self._app.status() == STATUS_ZOMBIE:
            return True

        return False

    def _handle_sig_fd(self, fd, dummy):
        """Handle read events for captured signals.

        :param fd: A file descriptor on which signal information will be sent.
        :type fd: int -- valid file descriptor.
        :param dummy: A dummy parameter.  Required for magic.
        """
        data = os.read(fd, 4)
        sig = struct.unpack('%uB' % len(data), data)
        if sig[0] == signal.SIGCHLD:
            utils.get_logger().info(utils._('SIGCHLD received'))
            if self._handle_child_died():
                raise StopIteration(utils._('launched program exited'))
        elif sig[0] == signal.SIGINT:
            utils.get_logger().info(utils._('SIGINT received'))
            raise StopIteration(utils._('keyboard interrupt'))
        elif sig[0] == signal.SIGTERM:
            utils.get_logger().info(utils._('SIGTERM received'))
            raise StopIteration(utils._('terminate'))
        else:
            utils.get_logger().warning(utils._('unknown signal {signal} received').format(signal=sig[0]))

    def _set_signal_handlers(self):
        """Set the signal handlers."""
        def noopSignalHandler(*args):
            pass
        self._sigchld_handler = signal.signal(signal.SIGCHLD, noopSignalHandler)
        self._sigint_handler  = signal.signal(signal.SIGINT,  noopSignalHandler)
        self._sigterm_handler = signal.signal(signal.SIGTERM, noopSignalHandler)

        sig_r_fd, sig_w_fd = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)
        signal.set_wakeup_fd(sig_w_fd)
        self._add_read_fd_handler(sig_r_fd, self._handle_sig_fd, None)

    def _shutdown(self):
        """Restore the previous state to the world when the Session is torn down."""
        signal.signal(signal.SIGCHLD, self._sigchld_handler)
        signal.signal(signal.SIGINT,  self._sigint_handler)
        signal.signal(signal.SIGTERM, self._sigterm_handler)

        for bridge_pair in self._config.socket_bridges:
            os.remove(translate_to_real_address(bridge_pair.session_address))

    def _stop_services(self):
        """Ask any started services to stop."""
        for service in self._child_processes:
            service.stop()
