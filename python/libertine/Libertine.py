# Copyright 2015 Canonical Ltd.
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

import abc
import contextlib
import crypt
import json
import lxc
import os
import shlex
import shutil
import subprocess
import libertine.utils

home_path = os.environ['HOME']


def check_lxc_net_entry(entry):
    lxc_net_file = open('/etc/lxc/lxc-usernet')
    found = False

    for line in lxc_net_file:
        if entry in line:
            found = True
            break

    return found


def setup_host_environment(username, password):
    lxc_net_entry = "%s veth lxcbr0 10" % str(username)

    if not check_lxc_net_entry(lxc_net_entry):
        passwd = subprocess.Popen(["sudo", "--stdin", "usermod", "--add-subuids", "100000-165536",
                                   "--add-subgids", "100000-165536", str(username)],
                                  stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.STDOUT)
        passwd.communicate((password + '\n').encode('UTF-8'))

        add_user_cmd = "echo %s | sudo tee -a /etc/lxc/lxc-usernet > /dev/null" % lxc_net_entry
        subprocess.Popen(add_user_cmd, shell=True)


def get_lxc_default_config_path():
    return os.path.join(home_path, '.config', 'lxc')


def get_container_distro(container_id):
    container_distro = ""

    with open(libertine.utils.get_libertine_database_file_path()) as fd:
        container_list = json.load(fd)

    for container in container_list["containerList"]:
        if container["id"] == container_id:
            return container["distro"]

    return ""


def get_host_architecture():
    dpkg = subprocess.Popen(['dpkg', '--print-architecture'],
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
    if dpkg.wait() != 0:
        parser.error("Failed to determine the local architecture.")

    return dpkg.stdout.read().strip()


def chown_recursive_dirs(path):
    uid = None
    gid = None

    if 'SUDO_UID' in os.environ:
        uid = int(os.environ['SUDO_UID'])
    if 'SUDO_GID' in os.environ:
        gid = int(os.environ['SUDO_GID'])

    if uid is not None and gid is not None:
        for root, dirs, files in os.walk(path):
            for d in dirs:
                os.chown(os.path.join(root, d), uid, gid)
            for f in files:
                os.chown(os.path.join(root, f), uid, gid)

        os.chown(path, uid, gid)


def create_libertine_user_data_dir(container_id):
    user_data = libertine.utils.get_libertine_container_userdata_dir_path(container_id)

    if not os.path.exists(user_data):
        os.makedirs(user_data)


def create_compiz_config(container_id):
    compiz_config_dir = os.path.join(libertine.utils.get_libertine_container_userdata_dir_path(container_id),
                                     '.config', 'compiz-1', 'compizconfig')

    if not os.path.exists(compiz_config_dir):
        os.makedirs(compiz_config_dir)

    # Create the general Compiz config file
    with open(os.path.join(compiz_config_dir, 'config'), 'w+') as fd:
        fd.write("[general]\n")
        fd.write("profile = Default\n")
        fd.write("integration = true\n")

    # Create the default profile file
    with open(os.path.join(compiz_config_dir, 'Default.ini'), 'w+') as fd:
        fd.write("[core]\n")
        fd.write("s0_active_plugins = core;place;\n\n")
        fd.write("[place]\n")
        fd.write("s0_mode = 3")


def lxc_container(container_id):
    config_path = libertine.utils.get_libertine_containers_dir_path()
    container = lxc.Container(container_id, config_path)

    return container


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
    return '/usr/bin/apt ' + apt_args_for_verbosity_level(verbosity) + ' '


class BaseContainer(metaclass=abc.ABCMeta):
    """
    An abstract base container to provide common functionality for all
    concrete container types.

    :param container_id: The machine-readable container name.
    """
    def __init__(self, container_id):
        self.container_id = container_id

    def create_libertine_container(self, password=None, verbosity=1):
        pass

    def destroy_libertine_container(self, verbosity=1):
        pass

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
        self.run_in_container(apt_command_prefix(verbosity) + 'update')
        self.run_in_container(apt_command_prefix(verbosity) + 'upgrade')

    def install_package(self, package_name, verbosity=1):
        """
        Installs a named package in the container.

        :param package_name: The name of the package as APT understands it.
        :param verbosity: the chattiness of the output on a range from 0 to 2
        """
        return self.run_in_container(apt_command_prefix(verbosity) + "install --no-install-recommends '" + package_name + "'") == 0


class LibertineLXC(BaseContainer):
    """
    A concrete container type implemented using an LXC container.
    """

    def __init__(self, container_id):
        super().__init__(container_id)
        self.container = lxc_container(container_id)
        self.series = get_container_distro(container_id)

    def is_running(self):
        return self.container.running

    def start_container(self):
        if not self.container.running:
            if not self.container.start():
                raise RuntimeError("Container failed to start")
            if not self.container.wait("RUNNING", 10):
                raise RuntimeError("Container failed to enter the RUNNING state")

        if not self.container.get_ips(timeout=30):
            raise RuntimeError("Not able to connect to the network.")

        self.run_in_container("umount /tmp/.X11-unix")

    def stop_container(self):
        self.container.stop()

    def run_in_container(self, command_string):
        cmd_args = shlex.split(command_string)
        return self.container.attach_wait(lxc.attach_run_command, cmd_args)

    def destroy_libertine_container(self):
        if self.container.defined:
            self.container.stop()
            self.container.destroy()

    def create_libertine_container(self, password=None, verbosity=1):
        if password is None:
            return

        installed_release = self.series

        username = os.environ['USER']
        user_id = os.getuid()
        group_id = os.getgid()

        setup_host_environment(username, password)

        # Generate the default lxc default config, if it doesn't exist
        config_path = get_lxc_default_config_path()
        config_file = "%s/default.conf" % config_path

        if not os.path.exists(config_path):
            os.mkdir(config_path)

        if not os.path.exists(config_file):
            with open(config_file, "w+") as fd:
                fd.write("lxc.network.type = veth\n")
                fd.write("lxc.network.link = lxcbr0\n")
                fd.write("lxc.network.flags = up\n")
                fd.write("lxc.network.hwaddr = 00:16:3e:xx:xx:xx\n")
                fd.write("lxc.id_map = u 0 100000 %s\n" % user_id)
                fd.write("lxc.id_map = g 0 100000 %s\n" % group_id)
                fd.write("lxc.id_map = u %s %s 1\n" % (user_id, user_id))
                fd.write("lxc.id_map = g %s %s 1\n" % (group_id, group_id))
                fd.write("lxc.id_map = u %s %s %s\n" % (user_id + 1, (user_id + 1) + 100000, 65536 - (user_id + 1)))
                fd.write("lxc.id_map = g %s %s %s\n" % (group_id + 1, (group_id + 1) + 100000, 65536 - (user_id + 1)))

        create_libertine_user_data_dir(self.container_id)

        # Figure out the host architecture
        architecture = get_host_architecture()

        if not self.container.create("download", 0,
                                     {"dist": "ubuntu",
                                      "release": installed_release,
                                      "arch": architecture}):
            return False

        self.create_libertine_config()

        if self.container.start():
            self.run_in_container("userdel-r ubuntu")
            self.run_in_container("useradd -u {} -p {} -G sudo {}".format(str(user_id), crypt.crypt(password), str(username)))

            if verbosity == 1:
                print("Updating the contents of the container after creation...")
            self.update_packages(verbosity)

            if verbosity == 1:
                print("Installing Compiz as the Xmir window manager...")
            self.install_package('compiz', verbosity)
            create_compiz_config(self.container.name)

            self.container.stop()
        else:
            raise RuntimeError("Container failed to start.")

    def create_libertine_config(self):
        user_id = os.getuid()
        home_entry = (
            "%s %s none bind,create=dir"
            % (libertine.utils.get_libertine_container_userdata_dir_path(self.container_id),
               home_path.strip('/'))
        )

        # Bind mount the user's home directory
        self.container.append_config_item("lxc.mount.entry", home_entry)

        xdg_user_dirs = ['Documents', 'Music', 'Pictures', 'Videos']

        for user_dir in xdg_user_dirs:
            xdg_user_dir_entry = (
                "%s/%s %s/%s none bind,create=dir,optional"
                % (home_path, user_dir, home_path.strip('/'), user_dir)
            )
            self.container.append_config_item("lxc.mount.entry", xdg_user_dir_entry)

        # Setup the mounts for /run/user/$user_id
        run_user_entry = "/run/user/%s run/user/%s none rbind,create=dir" % (user_id, user_id)
        self.container.append_config_item("lxc.mount.entry", "tmpfs run tmpfs rw,nodev,noexec,nosuid,size=5242880")
        self.container.append_config_item("lxc.mount.entry",
                                          "none run/user tmpfs rw,nodev,noexec,nosuid,size=104857600,mode=0755,create=dir")
        self.container.append_config_item("lxc.mount.entry", run_user_entry)

        self.container.append_config_item("lxc.include", "/usr/share/libertine/libertine-lxc.conf")

        # Dump it all to disk
        self.container.save_config()


class LibertineChroot(BaseContainer):
    """
    A concrete container type implemented using a plain old chroot.
    """

    def __init__(self, container_id):
        super().__init__(container_id)
        self.series = get_container_distro(container_id)
        self.chroot_path = libertine.utils.get_libertine_container_rootfs_path(container_id)
        os.environ['FAKECHROOT_CMD_SUBST'] = '$FAKECHROOT_CMD_SUBST:/usr/bin/chfn=/bin/true'
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'

    def run_in_container(self, command_string):
        cmd_args = shlex.split(command_string)
        if self.series == "trusty":
            proot_cmd = '/usr/bin/proot'
            if not os.path.isfile(proot_cmd) or not os.access(proot_cmd, os.X_OK):
                raise RuntimeError('executable proot not found')
            command_prefix = proot_cmd + " -b /usr/lib/locale -S " + self.chroot_path
        else:
            command_prefix = "fakechroot fakeroot chroot " + self.chroot_path
        args = shlex.split(command_prefix + ' ' + command_string)
        cmd = subprocess.Popen(args).wait()

    def destroy_libertine_container(self):
        shutil.rmtree(self.chroot_path)

    def create_libertine_container(self, password=None, verbosity=1):
        installed_release = self.series

        # Create the actual chroot
        if installed_release == "trusty":
            command_line = "debootstrap --verbose " + installed_release + " " + self.chroot_path
        else:
            command_line = "fakechroot fakeroot debootstrap --verbose --variant=fakechroot " + installed_release + " " + self.chroot_path
        args = shlex.split(command_line)
        subprocess.Popen(args).wait()

        # Remove symlinks as they can ill-behaved recursive behavior in the chroot
        if installed_release != "trusty":
            print("Fixing chroot symlinks...")
            os.remove(os.path.join(self.chroot_path, 'dev'))
            os.remove(os.path.join(self.chroot_path, 'proc'))

            with open(os.path.join(self.chroot_path, 'usr', 'sbin', 'policy-rc.d'), 'w+') as fd:
                fd.write("#!/bin/sh\n\n")
                fd.write("while true; do\n")
                fd.write("case \"$1\" in\n")
                fd.write("  -*) shift ;;\n")
                fd.write("  makedev) exit 0;;\n")
                fd.write("  *)  exit 101;;\n")
                fd.write("esac\n")
                fd.write("done\n")
                os.fchmod(fd.fileno(), 0o755)

        # Add universe and -updates to the chroot's sources.list
        if (get_host_architecture() == 'armhf'):
            archive = "deb http://ports.ubuntu.com/ubuntu-ports "
        else:
            archive = "deb http://archive.ubuntu.com/ubuntu "

        if verbosity == 1:
            print("Updating chroot's sources.list entries...")
        with open(os.path.join(self.chroot_path, 'etc', 'apt', 'sources.list'), 'a') as fd:
            fd.write(archive + installed_release + " universe\n")
            fd.write(archive + installed_release + "-updates main\n")
            fd.write(archive + installed_release + "-updates universe\n")

        create_libertine_user_data_dir(self.container_id)

        if installed_release == "trusty":
            print("Additional configuration for Trusty chroot...")

            proot_cmd = '/usr/bin/proot'
            if not os.path.isfile(proot_cmd) or not os.access(proot_cmd, os.X_OK):
                raise RuntimeError('executable proot not found')
            cmd_line_prefix = proot_cmd + " -b /usr/lib/locale -S " + self.chroot_path

            command_line = cmd_line_prefix + " dpkg-divert --local --rename --add /etc/init.d/systemd-logind"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " dpkg-divert --local --rename --add /sbin/initctl"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " dpkg-divert --local --rename --add /sbin/udevd"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " dpkg-divert --local --rename --add /usr/sbin/rsyslogd"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " ln -s /bin/true /etc/init.d/systemd-logind"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " ln -s /bin/true /sbin/initctl"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " ln -s /bin/true /sbin/udevd"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " ln -s /bin/true /usr/sbin/rsyslogd"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

        if verbosity == 1:
            print("Updating the contents of the container after creation...")
        self.update_packages(verbosity)
        self.install_package("libnss-extrausers", verbosity)

        if verbosity == 1:
            print("Installing Compiz as the Xmir window manager...")
        self.install_package("compiz", verbosity)
        create_compiz_config(self.container_id)

        # Check if the container was created as root and chown the user directories as necessary
        chown_recursive_dirs(libertine.utils.get_libertine_container_userdata_dir_path(self.container_id))


class LibertineMock(BaseContainer):
    """
    A concrete mock container type.  Used for unit testing.
    """
    def __init__(self, container_id):
        super().__init__(container_id)

    def run_in_container(self, command_string):
        return 0


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

    def __init__(self, container_id, container_type="lxc"):
        """
        Initializes the container object.

        :param container_id: The machine-readable container name.
        :param container_type: One of the supported container types (lxc,
            chroot, mock).
        """
        super().__init__()
        if container_type == "lxc":
            self.container = LibertineLXC(container_id)
        elif container_type == "chroot":
            self.container = LibertineChroot(container_id)
        elif container_type == "mock":
            self.container = LibertineMock(container_id)
        else:
            raise RuntimeError("Unsupported container type %s" % container_type)

    def destroy_libertine_container(self):
        """
        Destroys the container and releases all its system resources.
        """
        self.container.destroy_libertine_container()

    def create_libertine_container(self, password=None, verbosity=1):
        """
        Creates the container.
        """
        self.container.create_libertine_container(password, verbosity)

    def update_libertine_container(self, verbosity=1):
        """
        Updates the contents of the container.
        """
        with ContainerRunning(self.container):
            self.container.update_packages(verbosity)

    def install_package(self, package_name, verbosity=1):
        """
        Installs a package in the container.
        """
        with ContainerRunning(self.container):
            return self.container.install_package(package_name, verbosity)

    def remove_package(self, package_name, verbosity=1):
        """
        Removes a package from the container.

        :param package_name: The name of the package to be removed.
        :param verbosity: The verbosity level of the progress reporting.
        """
        with ContainerRunning(self.container):
            self.container.run_in_container(apt_command_prefix(verbosity) + "remove '" + package_name + "'") == 0

    def search_package_cache(self, search_string):
        """
        Searches the container's package cache for a named package.

        :param search_string: the (regex) to use to search the package cache.
            The regex is quoted to sanitize it.
        """
        with ContainerRunning(self.container):
            self.container.run_in_container("/usr/bin/apt-cache search '" + search_string + "'")
