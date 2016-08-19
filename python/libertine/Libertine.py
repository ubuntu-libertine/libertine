# Copyright 2015-2106 Canonical Ltd.
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

from .AppDiscovery import AppLauncherCache
from gi.repository import Libertine
from multiprocessing import Process, active_children
from socket import *
import abc
import contextlib
import libertine.utils
import os
import psutil
import select
import shutil
import shlex
import signal
import sys
import time

from libertine.ContainersConfig import ContainersConfig
from libertine.HostInfo import HostInfo


def apt_args_for_verbosity_level(verbosity):
    """
    Maps numeric verbosity levels onto APT command-line arguments.

    :param verbosity: 0 is quiet, 1 is normal, 2 is incontinent
    """
    return {
            0: '--quiet=2',
            1: '--assume-yes',
            2: '--quiet=1 --assume-yes --option APT::Status-Fd=1'
    }.get(verbosity, '')


def apt_command_prefix(verbosity):
    return '/usr/bin/apt-get ' + apt_args_for_verbosity_level(verbosity) + \
           ' --option Apt::Cmd::Disable-Script-Warning=true --option Dpkg::Progress-Fancy=1' + \
           ' --option Apt::Color=1 '


def handle_runtime_error(error):
    print("%s" % error)
    return False


class BaseContainer(metaclass=abc.ABCMeta):
    """
    An abstract base container to provide common functionality for all
    concrete container types.

    :param container_id: The machine-readable container name.
    """
    def __init__(self, container_id):
        self.container_type = 'unknown'
        self.container_id = container_id
        self.root_path = libertine.utils.get_libertine_container_rootfs_path(self.container_id)
        self.default_packages = ['matchbox',
                                 'libnss-extrausers',
                                 'humanity-icon-theme',
                                 'maliit-inputcontext-gtk2',
                                 'maliit-inputcontext-gtk3',
                                 'maliit-framework']

    def create_libertine_container(self, password=None, multiarch=False, verbosity=1):
        pass

    def destroy_libertine_container(self, verbosity=1):
        pass

    def copy_package_to_container(self, package_path):
        """
        Copies a Debian package from the host to a pre-determined place
        in a container.

        :param package_path: The full path to the Debian package located
                             on the host.
        """
        if os.path.exists(os.path.join(self.root_path, 'tmp', package_path.split('/')[-1])):
            return False

        shutil.copy2(package_path, os.path.join(self.root_path, 'tmp'))
        return True

    def delete_package_in_container(self, package_path):
        """
        Deletes a previously copied in Debian package in a container.

        :param package_path: The full path to the Debian package located
                             on the host.
        """
        os.remove(os.path.join(self.root_path, 'tmp', package_path.split('/')[-1]))

    def is_running(self):
        """
        Indicates if the container is 'running'. The definition of 'running'
        depends on the type of the container.
        """
        return False

    def start_container(self):
        """
        Starts the container.  To start the container means to put it into a
        'running' state, the meaning of which depends on the type of the
        container.
        """
        pass

    def stop_container(self):
        """
        Stops the container.  The opposite of start_container().
        """
        pass

    @abc.abstractmethod
    def run_in_container(self, command_string):
        """
        Runs a command inside the container context.

        :param command_string: The command line to execute in the container context.
        """
        pass

    def update_packages(self, verbosity=1):
        """
        Updates all packages installed in the container.

        :param verbosity: the chattiness of the output on a range from 0 to 2
        """
        self.run_in_container(apt_command_prefix(verbosity) + '--force-yes update')
        return self.run_in_container(apt_command_prefix(verbosity) + '--force-yes dist-upgrade')

    def install_package(self, package_name, verbosity=1, readline=False):
        """
        Installs a named package in the container.

        :param package_name: The name of the package as APT understands it or
                             a full path to a Debian package on the host.
        :param verbosity: the chattiness of the output on a range from 0 to 2
        """
        if package_name.endswith('.deb'):
            delete_package = self.copy_package_to_container(package_name)

            self.run_in_container('ls -la ' + os.environ['HOME'])
            self.run_in_container('dpkg -i ' +
                os.path.join('/', 'tmp', package_name.split('/')[-1]))

            ret = self.run_in_container(apt_command_prefix(verbosity) + " install -f") == 0

            if delete_package:
                self.delete_package_in_container(package_name)

            return ret
        else:
            if readline:
                os.environ['DEBIAN_FRONTEND'] = 'readline'
            return self.run_in_container(apt_command_prefix(verbosity) + " install '" + package_name + "'") == 0

    def configure_multiarch(self, should_enable, verbosity=1):
        """
        Enables or disables multiarch repositories.

        :param should_enable: Whether or not to enable multiarch support.
        :param verbosity: the chattiness of the output on a range from 0 to 2
        """
        if should_enable:
            ret = self.run_in_container("dpkg --add-architecture i386")
            if ret or ret == 0:
                self.run_in_container(apt_command_prefix(verbosity) + '--force-yes update')
            return ret
        else:
            self.run_in_container(apt_command_prefix(verbosity) + "purge \".*:i386\"")
            return self.run_in_container("dpkg --remove-architecture i386")

    def configure_add_archive(self, archive, public_key_file, verbosity=1):
        """
        Adds the given archive. If this archive requires a key, prompt user.

        :param archive: The configuration command to run.
        :param public_key_file: file containing the public key used to sign this archive
        :param verbosity: the chattiness of the output on a range from 0 to 2
        """
        if not os.path.exists(os.path.join(self.root_path, 'usr', 'bin', 'add-apt-repository')):
            self.update_packages(verbosity)
            self.install_package("software-properties-common", verbosity)
        if 'https://' in archive and not os.path.exists(os.path.join(self.root_path, 'usr', 'lib', 'apt', 'methods', 'https')):
            self.update_packages(verbosity)
            self.install_package("apt-transport-https", verbosity)

        retcode = self.run_in_container("add-apt-repository -y " + archive)
        if retcode is 0 and public_key_file is not None:
            with open(public_key_file, 'r') as keyfile:
                return self.run_in_container("bash -c 'echo \"%s\" | apt-key add -'" % keyfile.read())

        return retcode

    def configure_remove_archive(self, archive, verbosity=1):
        """
        Removes the given archive.

        :param archive: The configuration command to run.
        :param verbosity: the chattiness of the output on a range from 0 to 2
        """
        return self.run_in_container("add-apt-repository -y -r " + archive)

    @property
    def name(self):
        """
        The human-readable name of the container.
        """
        name = Libertine.container_name(self.container_id)
        if not name:
            name = 'Unknown'
        return name


class LibertineMock(BaseContainer):
    """
    A concrete mock container type.  Used for unit testing.
    """
    def __init__(self, container_id):
        super().__init__(container_id)
        self.container_type = "mock"

    def create_libertine_container(self, password=None, multiarch=False, verbosity=1):
        return True

    def run_in_container(self, command_string):
        return 0

    def launch_application(self, app_exec_line):
        import subprocess

        cmd = subprocess.Popen(app_exec_line)
        cmd.wait()


class ContainerRunning(contextlib.ExitStack):
    """
    Helper object providing a running container context.

    Starts the container running if it's not already running, and shuts it down
    when the context is destroyed if it was not running at context creation.
    """
    def __init__(self, container):
        super().__init__()
        if not container.is_running():
            container.start_container()
            self.callback(lambda: container.stop_container())


class LibertineContainer(object):
    """
    A sandbox for DEB-packaged X11-based applications.
    """

    def __init__(self, container_id):
        """
        Initializes the container object.

        :param container_id: The machine-readable container name.
        """
        super().__init__()

        self.containers_config = ContainersConfig()

        container_type = self.containers_config.get_container_type(container_id)

        if container_type == None or container_type == "lxc":
            from  libertine.LxcContainer import LibertineLXC
            self.container = LibertineLXC(container_id)
        elif container_type == "chroot":
            from  libertine.ChrootContainer import LibertineChroot
            self.container = LibertineChroot(container_id)
        elif container_type == "mock":
            self.container = LibertineMock(container_id)
        else:
            raise RuntimeError("Unsupported container type %s" % container_type)

    @property
    def container_id(self):
        return self.container.container_id

    @property
    def name(self):
        return self.container.name

    @property
    def container_type(self):
        return self.container.container_type

    @property
    def root_path(self):
        return self.container.root_path

    def destroy_libertine_container(self):
        """
        Destroys the container and releases all its system resources.
        """
        return self.container.destroy_libertine_container()

    def create_libertine_container(self, password=None, multiarch=False, verbosity=1):
        """
        Creates the container.
        """
        self.container.architecture = HostInfo().get_host_architecture()
        self.container.installed_release = self.containers_config.get_container_distro(self.container_id)

        return self.container.create_libertine_container(password, multiarch, verbosity)

    def update_libertine_container(self, verbosity=1):
        """
        Updates the contents of the container.
        """
        try:
            with ContainerRunning(self.container):
                return self.container.update_packages(verbosity)
        except RuntimeError as e:
            return handle_runtime_error(e)

    def install_package(self, package_name, verbosity=1, readline=False):
        """
        Installs a package in the container.
        """
        try:
            with ContainerRunning(self.container):
                return self.container.install_package(package_name, verbosity, readline)
        except RuntimeError as e:
            return handle_runtime_error(e)

    def remove_package(self, package_name, verbosity=1, readline=False):
        """
        Removes a package from the container.

        :param package_name: The name of the package to be removed.
        :param verbosity: The verbosity level of the progress reporting.
        """
        try:
            with ContainerRunning(self.container):
                if readline:
                    os.environ['DEBIAN_FRONTEND'] = 'readline'

                if self.container.run_in_container(apt_command_prefix(verbosity) + " purge '" + package_name + "'") != 0:
                    return False
                return self.container.run_in_container(apt_command_prefix(verbosity) + "autoremove --purge") == 0
        except RuntimeError as e:
            return handle_runtime_error(e)

    def search_package_cache(self, search_string):
        """
        Searches the container's package cache for a named package.

        :param search_string: the (regex) to use to search the package cache.
            The regex is quoted to sanitize it.
        """
        try:
            with ContainerRunning(self.container):
                return self.container.run_in_container("/usr/bin/apt-cache search '" + search_string + "'")
        except RuntimeError as e:
            return handle_runtime_error(e)

    def launch_application(self, app_exec_line):
        """
        Launches an application in the container.

        :param app_exec_line: the application exec line as passed in by
            ubuntu-app-launch
        """
        if self.containers_config.container_exists(self.container.container_id):
            # Update $PATH as necessary
            if '/usr/games' not in os.environ['PATH']:
                os.environ['PATH'] = os.environ['PATH'] + ":/usr/games"

            self.container.launch_application(app_exec_line)
        else:
            raise RuntimeError("Container with id %s does not exist." % self.container.container_id)

    def list_app_launchers(self, use_json=False):
        """
        Enumerates all application launchers (based on .desktop files) available
        in the container.

        :param use_json: Indicates the returned string should be i JSON format.
            The default format is some human-readble format.
        :rtype: A printable string containing a list of application launchers
            available in the container.
        """
        if use_json:
            return AppLauncherCache(self.container.name,
                                    self.container.root_path).to_json()
        else:
            return str(AppLauncherCache(self.container.name,
                                        self.container.root_path))

    def exec_command(self, exec_line):
        """
        Runs an arbitrary application in the container.  Mainly used for status
        reporting, etc. in the container.

        :param exec_line: The exec line to run inside the container.  For
            example, 'apt-cache policy package-foo'
        :rtype: The output of the given command.
        """
        try:
            with ContainerRunning(self.container):
                return self.container.run_in_container(exec_line) == 0
        except RuntimeError as e:
            return handle_runtime_error(e)

    def configure_multiarch(self, should_enable, verbosity=1):
        try:
            with ContainerRunning(self.container):
                return self.container.configure_multiarch(should_enable, verbosity)
        except RuntimeError as e:
            return handle_runtime_error(e)

    def configure_add_archive(self, archive, key, verbosity):
        try:
            with ContainerRunning(self.container):
                return self.container.configure_add_archive(archive, key, verbosity)
        except RuntimeError as e:
            return handle_runtime_error(e)

    def configure_remove_archive(self, archive, verbosity):
        try:
            with ContainerRunning(self.container):
                return self.container.configure_remove_archive(archive, verbosity)
        except RuntimeError as e:
            return handle_runtime_error(e)


class Socket(object):
    """
    A simple socket wrapper class. This will wrap a socket

    :param socket: A python socket to be wrapped
    """
    def __init__(self, sock):
        if not isinstance(sock, socket):
             raise TypeError("expected socket to be a python socket class instead found: '{}'".format(sock.__class__))

        self.socket = sock

    """
    Implement equality checking for other instances of this class or ints only.

    :param other: Either a Socket class or an int
    """
    def __eq__(self, other):
        if isinstance(other, Socket):
            return self.socket == other.socket
        elif isinstance(other, socket):
            return self.socket == other
        elif isinstance(other, int):
            return self.socket.fileno() == other
        else:
             raise TypeError("unsupported operand type(s) for ==: '{}' and '{}'".format(self.__class__, type(other)))

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return self.socket.fileno()

    def socket(self):
        return self.socket

class SessionSocket(Socket):
    """
    Creates a AF_UNIX socket from a path to be used as the session socket.
    This is used for RAII and to take ownership of the socket

    :param path: The path the socket will be binded with
    """
    def __init__(self, session_path):
        try:
            sock = socket(AF_UNIX, SOCK_STREAM)
        except:
            sock = None
            raise
        else:
            try:
                sock.bind(session_path)
                sock.listen(5)
            except:
                sock.close()
                sock = None
                raise
            else:
                super().__init__(sock)
                self.session_path = session_path

    def __del__(self):
        self.socket.shutdown(SHUT_RDWR)
        self.socket.close()
        os.remove(self.session_path)


class HostSessionSocketPair():
    def __init__(self, host_socket_path, session_socket_path):
        self.host_socket_path    = host_socket_path
        self.session_socket_path = session_socket_path


class LibertineSessionBridge(object):
    """
    Creates a session bridge which will pair host and session sockets to proxy the info
    from the session to the host and vice versa.

    :param host_session_socket_paths: A list of pairs container valid sockets to proxy {host:session}
    """
    def __init__(self, host_session_socket_paths):
        self.descriptors = []
        self.host_session_socket_path_map = {}
        self.socket_pairs = {}

        for host_session_socket_pair in host_session_socket_paths:
            host_path    = host_session_socket_pair.host_socket_path
            session_path = host_session_socket_pair.session_socket_path

            socket = SessionSocket(session_path)

            self.descriptors.append(socket)
            self.host_session_socket_path_map.update({socket:host_path})

    """
    If we end up going out of scope/error let's make sure we clean up sockets and paths.
    """
    def __del__(self):
        self.socket_pairs = None
        self.descriptors  = None
        self.host_session_socket_path_map = None

    """
    When a new connection is made on one of the main sockets we have to create a new
    socket pairing with the container socket.

    :param host_path:      The raw path to the container socket
    :param container_sock: The socket which received a new connection
    """
    def accept_new_connection(self, host_path, container_sock):
        newconn = Socket(container_sock.accept()[0])
        self.descriptors.append(newconn)

        host_sock = Socket(socket(AF_UNIX, SOCK_STREAM))
        host_sock.socket.connect(host_path)
        self.descriptors.append(host_sock)

        self.socket_pairs.update({newconn:host_sock})
        self.socket_pairs.update({host_sock:newconn})

    """
    Cleans up a socket that has had its connection closed.

    :param socket_to_remove: The socket that had its connection closed
    """
    def close_connections(self, socket_to_remove):
        partner_socket = self.socket_pairs[socket_to_remove.fileno()]

        self.socket_pairs.pop(socket_to_remove.fileno())
        self.socket_pairs.pop(partner_socket.socket.fileno())

        self.descriptors.remove(socket_to_remove)
        self.descriptors.remove(partner_socket)

        if socket_to_remove in self.host_session_socket_path_map:
            self.host_session_socket_path_map.pop(socket_to_remove)

    """
    The main loop which uses select to block until one of the sockets we are listening to becomes readable.
    It is advised this be started in its own process or thread, as this function blocks!
    """
    def main_loop(self):
        while 1:
            try:
                raw_sockets = list(map(lambda x : x.socket, self.descriptors))
                rlist, wlist, elist = select.select(raw_sockets, [], [])
            except InterruptedError as e:
                continue
            except Exception as e:
                libertine.utils.get_logger().exception(e)
                break

            for sock in rlist:
                if sock.fileno() == -1:
                    continue

                # Its possible to have multiple socket reads that are pairs. If this happens and we remove a pair we
                # need to ignore the other pair since it no longer has a complete pair
                if sock.fileno() not in self.host_session_socket_path_map and sock.fileno() not in self.socket_pairs:
                    continue

                if sock.fileno() in self.host_session_socket_path_map:
                    self.accept_new_connection(self.host_session_socket_path_map[sock.fileno()], sock)

                else:
                    try:
                        data = sock.recv(4096)
                    except Exception as e:
                        libertine.utils.get_logger().exception(e)
                        self.close_connections(sock)
                        continue
                    else:
                        if len(data) == 0:
                            self.close_connections(sock)
                            continue

                    send_sock = self.socket_pairs[sock.fileno()].socket

                    if send_sock.fileno() < 0:
                        continue

                    totalsent = 0
                    while totalsent < len(data):
                        try:
                            sent = send_sock.send(data)
                        except BrokenPipeError as e:
                            libertine.utils.get_logger().exception(e)
                            self.close_connections(sock)
                            break
                        else:
                            if sent == 0:
                                close_connections(sock)
                                break
                            totalsent = totalsent + sent


class LibertineApplication(object):
    """
    Launches a libertine container with a session bridge for sockets such as dbus

    :param container_id: The container id.
    :param app_exec_line: The exec line used to start the app in the container.
    """
    def __init__(self, container_id, app_exec_line):
        signal.signal(signal.SIGTERM, self.cleanup_lsb)
        signal.signal(signal.SIGINT,  self.cleanup_lsb)

        self.container_id  = container_id
        self.app_exec_line = app_exec_line
        self.lsb           = None

    def cleanup_lsb(self, signum, frame):
        self.close_lsb()

    def close_lsb(self):
        if self.lsb is not None:
            self.lsb_process.terminate()

        while active_children():
            time.sleep(1)

    """
    Launches the libertine session bridge. This creates a proxy socket to read to and from
    for abstract sockets such as dbus.

    :param session_socket_paths: A list of socket paths the session will create.
    """
    def launch_session_bridge(self, session_socket_paths):
        self.lsb         = LibertineSessionBridge(session_socket_paths)
        self.lsb_process = Process(target=self.lsb.main_loop)
        self.lsb_process.start()

    """
    Launches the container from the id and attempts to run the application exec.
    """
    def launch_application(self):
        if not ContainersConfig().container_exists(self.container_id):
            raise RuntimeError("Container ID %s does not exist." % self.container_id)

        container = LibertineContainer(self.container_id)
        try:
            container.launch_application(self.app_exec_line)
        except:
            raise
        finally:
            self.close_lsb()
