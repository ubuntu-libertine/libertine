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
import abc
import contextlib
import json
import libertine.utils
import os
import shutil


def get_container_type(container_id):
    """
    Retrieves the type of container for a given container ID.
    :param container_id: The Container ID to search for.
    """
    try:
        with open(libertine.utils.get_libertine_database_file_path()) as fd:
            container_list = json.load(fd)

        for container in container_list["containerList"]:
            if container["id"] == container_id:
                return container["type"]

    except FileNotFoundError:
        pass

    # Return lxc as the default container type
    return "lxc"


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
        self.default_packages = ['matchbox', 'libnss-extrausers', 'software-properties-common',
                                 'humanity-icon-theme']

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
        self.run_in_container(apt_command_prefix(verbosity) + '--force-yes upgrade')

    def install_package(self, package_name, verbosity=1, extra_apt_args=""):
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

            ret = self.run_in_container(apt_command_prefix(verbosity) +
                    extra_apt_args + " install -f") == 0

            if delete_package:
                self.delete_package_in_container(package_name)

            return ret
        else:
            return self.run_in_container(apt_command_prefix(verbosity) +
                    extra_apt_args + " install '" + package_name + "'") == 0

    def configure_command(self, command, *args, verbosity=1):
        """
        Configures the container based on what the command is.

        :param command: The configuration command to run.
        :param *args: List of arguments used for the given configuration command
        """
        if command == 'multiarch':
            if args[0] == 'enable':
                ret = self.run_in_container("dpkg --add-architecture i386")
                if ret or ret == 0:
                    self.run_in_container(apt_command_prefix(verbosity) + '--force-yes update')
                return ret
            else:
                self.run_in_container(apt_command_prefix(verbosity) + "purge \".*:i386\"")
                return self.run_in_container("dpkg --remove-architecture i386")

        elif command == 'add-archive':
            if not os.path.exists(os.path.join(self.root_path, 'usr', 'bin', 'add-apt-repository')):
                self.update_packages(verbosity)
                self.install_package("software-properties-common", verbosity)

            return self.run_in_container("add-apt-repository -y " + args[0])

        elif command == 'delete-archive':
            return self.run_in_container("add-apt-repository -y -r " + args[0])

    def get_container_distro(self, container_id):
        """
        Retrieves the distro code name for a given container ID.

        :param container_id: The Container ID to search for.
        """
        with open(libertine.utils.get_libertine_database_file_path()) as fd:
            container_list = json.load(fd)

        for container in container_list["containerList"]:
            if container["id"] == container_id:
                return container["distro"]

        return ""

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

        container_type = get_container_type(container_id)

        if container_type == "lxc":
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
        self.container.destroy_libertine_container()

    def create_libertine_container(self, password=None, multiarch=False, verbosity=1):
        """
        Creates the container.
        """
        return self.container.create_libertine_container(password, multiarch, verbosity)

    def update_libertine_container(self, verbosity=1):
        """
        Updates the contents of the container.
        """
        try:
            with ContainerRunning(self.container):
                self.container.update_packages(verbosity)
        except RuntimeError as e:
            return handle_runtime_error(e)

    def install_package(self, package_name, verbosity=1):
        """
        Installs a package in the container.
        """
        try:
            with ContainerRunning(self.container):
                return self.container.install_package(package_name, verbosity)
        except RuntimeError as e:
            return handle_runtime_error(e)

    def remove_package(self, package_name, verbosity=1):
        """
        Removes a package from the container.

        :param package_name: The name of the package to be removed.
        :param verbosity: The verbosity level of the progress reporting.
        """
        try:
            with ContainerRunning(self.container):
                if self.container.run_in_container(apt_command_prefix(verbosity) + "purge '" + package_name + "'") != 0:
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
        if libertine.utils.container_exists(self.container.container_id):
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

    def configure_command(self, command, *args):
        try:
            with ContainerRunning(self.container):
                return self.container.configure_command(command, *args)
        except RuntimeError as e:
            return handle_runtime_error(e)
