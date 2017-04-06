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

"""Configure the libertine launcher."""

import argparse
import dbus
import os
import random
import string
import sys
from .task import TaskType, TaskConfig
from .. import utils

log = utils.get_logger()


def _generate_unique_id():
    """Generate a (hopefully) unique identifier string."""
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(8))


class SocketBridge(object):
    """Configuration for a single socket bridge entry.

    This is a 3-tuple of a label, the address of a Unix-domain socket in the
    host environment, and the address of a Unix-domain socket in the session
    environment.

    .. data:: env_var

       The label of the socket bridge.  This is used as the environment variable
       in the session environment.  It should follow the naming rules for
       environment variables.

    .. data:: host_address

        The address of a Unix-domain socket in the host environment.

    .. data:: session_address

        The address of a Unix-domain socket in the session environment.

    """

    def __init__(self, env_var, host_address, session_address):
        """Initialize the socket bridge address pair.

        :param env_var: The socket bridge label.
        :param host_address: The host socket address.
        :param session_address: The session socket address.

        """
        self.env_var         = env_var
        self.host_address    = host_address
        self.session_address = session_address

    def __repr__(self):
        """Get a human-readable string representation."""
        return '{{{}:{}->{}}}'.format(self.env_var, self.host_address, self.session_address)


def _get_maliit_address_from_dbus():
    """Query the session D-Bus for the address of the Maliit server.

    If there is no response from the D-Bus (let's just say there is no maliit
    server running) None is returned.
    """
    try:
        address_bus_name    = 'org.maliit.server'
        address_object_path = '/org/maliit/server/address'
        address_interface   = 'org.maliit.Server.Address'
        address_property    = 'address'

        session_bus   = dbus.SessionBus()
        maliit_object = session_bus.get_object('org.maliit.server', '/org/maliit/server/address')
        interface = dbus.Interface(maliit_object, dbus.PROPERTIES_IFACE)
        return interface.Get('org.maliit.Server.Address', 'address')
    except Exception as ex:
        log.warning(ex)
        return None


class Config(object):
    """Configuration for the libertine application launcher.

    The main configuration items are the container ID and the application
    command line.  Additional configuration items include and environment
    variables to be passed in to the application session and any sockets to be
    bridged between the session and the host.

    The following members can be read from objects of this class.

    ==================  ==================
    Attribute           Description
    ------------------  ------------------
    **id**              A unique session identifier.  A random string of letters and numbers.
    **container_id**    The ID of the container in which the session will run.
    **exec_line**       The program and arguments to execute.
    **host_environ**    A sanitized dictionary of environment variables to
                        export in host operations.
    **session_environ** A sanitized, remapped, and extended dictionary of environment variables to
                        export in the session environment.  Effectively a copy of the host
                        environment but with some changes.
    **socket_bridges**  A collection of SocketBridge objects to implement.
    **prelaunch_tasks** A collection of tasks to perform before launching the application.
    ==================  ==================

    """

    def __init__(self, argv=sys.argv[1:]):
        """
        :param argv: Command-line arguments used to configure the launcher.  Default is ``sys.argv``.

        """
        log.debug('Config.__init__() begins')
        arg_parser = argparse.ArgumentParser(description=utils._('Launch an application natively or in a Libertine container'))
        arg_parser.add_argument('-i', '--id',
                                help=utils._('Container identifier when launching containerized apps'))
        arg_parser.add_argument('-E', '--env',
                                default=[],
                                dest='environ',
                                action='append',
                                help=utils._('Set an environment variable'))
        arg_parser.add_argument('app_exec_line',
                                nargs=argparse.REMAINDER,
                                help=utils._('exec line'))
        options = arg_parser.parse_args(args=argv)

        if not options.app_exec_line:
            arg_parser.error(utils._('Must specify an exec line'))

        if options.id:
            self.container_id = options.id
        else:
            self.container_id = None

        self.id              = _generate_unique_id()
        self.exec_line       = options.app_exec_line
        self.host_environ    = self._sanitize_host_environment(options)
        self.socket_bridges  = self._create_socket_bridges()
        self.prelaunch_tasks = self._add_prelaunch_tasks()
        self.session_environ = self._generate_session_environment()

        log.debug('id = "{}"'.format(self.id))
        log.debug('container_id = "{}"'.format(self.container_id))
        log.debug('exec_line = "{}"'.format(self.exec_line))
        log.debug('session_environ = {}'.format(self.session_environ))
        for bridge in self.socket_bridges:
            log.debug('socket bridge: {}'.format(bridge))
        log.debug('Config.__init__() ends')

    def _sanitize_host_environment(self, options):
        """Create a dictionary of sanitized environment variables.

        The environment available in the Libertine aegis are effectively those
        of the launcher, but santized to remove any unwanted or dangerous stuff
        and with and changes requested on the command line.

        :param options: A collection of option values including a dictionary
                        named 'environ'.
        :param type: An argparse namespace.

        :returns: A sanitized host environment dictionary.
        """
        # inherit from the host
        environ = os.environ.copy()

        # remove problematic environment variables
        for e in ['QT_QPA_PLATFORM', 'XDG_DATA_DIRS', 'FAKECHROOT_BASE', 'FAKECHROOT_CMD_SUBST']:
            if e in environ:
                del environ[e]

        # add or replace CLI-speicifed variables
        for e in options.environ:
            k, v = e.split(sep='=', maxsplit=2)
            environ[k] = v

        return environ

    def _generate_session_environment(self):
        """Generate the session environment."""

        # Start with the host environment.
        environ = self.host_environ.copy()

        # Fudge some values.
        path = environ.get('PATH', '/usr/bin')
        if '/usr/games' not in path.split(sep=':'):
            environ['PATH'] = path + os.pathsep + '/usr/games'

        # Add the remapped socket bridge variables.
        for bridge in self.socket_bridges:
            environ[bridge.env_var] = 'unix:path=' + bridge.session_address

        return environ

    def _add_prelaunch_tasks(self):
        """Create a collection of pre-launch tasks."""
        tasks = []
        tasks.append(TaskConfig(TaskType.LAUNCH_SERVICE, ["pasted"]))

        return tasks

    def _create_socket_bridges(self):
        """Create the required socket bridge configs."""
        bridges = []

        if self.container_id:
            maliit_host_bridge = self._create_maliit_host_bridge()
            if maliit_host_bridge:
                bridges.append(maliit_host_bridge)
            dbus_host_bridge = self._create_dbus_host_bridge()
            if dbus_host_bridge:
                bridges.append(dbus_host_bridge)

        return bridges

    def _generate_session_socket_name(self, socket_target):
        """Generate a socket name for the target.

        :param target: A string used as a base for the socket address.

        If there is a seession ID, the session ID is appended to the socket name
        to make it (hopefully) unique.
        """
        socket_name = os.path.join(utils.get_libertine_runtime_dir(), socket_target)
        if self.id:
            socket_name += ('-' + self.id)
        return socket_name

    def _get_dbus_host_address(self):
        """Get (or try to get) the D-Bus server socket address.

        If the D-Bus server socket address environment variable is set, the
        value of that environment variable is used, otherwise None is returned.
        """
        return self.host_environ.get('DBUS_SESSION_BUS_ADDRESS', None)

    def _create_dbus_host_bridge(self):
        """Create a socket bridge for the D-Bus session.

        Creates a socket bridge configuration for the D-Bus session, if a socket
        can be found for the host, otherwise returns None.
        """
        socket_bridge = None
        server_address = self._get_dbus_host_address()
        if server_address:
            socket_bridge = SocketBridge('DBUS_SESSION_BUS_ADDRESS',
                                         server_address,
                                         self._generate_session_socket_name('dbus'))
        return socket_bridge

    def _get_maliit_host_address(self):
        """Get (or try to get) the Maliit server socket address.

        If the Maliit server socket address environment variable is set, the
        value of that environment variable is used, otherwise an attempt is made
        to query the session D-Bus.  If neither works, Maliit is probably not
        there.
        """
        env_var = self.host_environ.get('MALIIT_SERVER_ADDRESS', None)
        if env_var:
            return env_var
        return _get_maliit_address_from_dbus()

    def _create_maliit_host_bridge(self):
        """Create a socket bridge for the Maliit server.

        Creates a socket bridge configuration for the Maliit server, if a socket
        can be found for the host, otherwise returns None.
        """
        socket_bridge = None
        server_address = self._get_maliit_host_address()
        if server_address:
            socket_bridge = SocketBridge('MALIIT_SERVER_ADDRESS',
                                         server_address,
                                         self._generate_session_socket_name('maliit'))
        return socket_bridge
