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

import crypt
import lxc
import os
import psutil
import shlex
import subprocess
import sys
import tempfile

from .Libertine import BaseContainer
from . import utils
from socket import *


home_path = os.environ['HOME']


def check_lxc_net_entry(entry):
    lxc_net_file = open('/etc/lxc/lxc-usernet')
    found = False

    for line in lxc_net_file:
        if entry in line:
            found = True
            break

    return found


def setup_host_environment(username):
    lxc_net_entry = "%s veth lxcbr0 10" % str(username)

    if not check_lxc_net_entry(lxc_net_entry):
        subprocess.Popen(["sudo", "libertine-lxc-setup", str(username)]).wait()


def get_lxc_default_config_path():
    return os.path.join(home_path, '.config', 'lxc')


def lxc_container(container_id):
    config_path = utils.get_libertine_containers_dir_path()
    if not os.path.exists(config_path):
        os.makedirs(config_path)

    container = lxc.Container(container_id, config_path)

    return container


def get_host_timezone():
    with open(os.path.join('/', 'etc', 'timezone'), 'r') as fd:
        host_timezone = fd.read().strip('\n')

    return host_timezone


class LibertineLXC(BaseContainer):
    """
    A concrete container type implemented using an LXC container.
    """

    def __init__(self, container_id):
        super().__init__(container_id)
        self.container_type = "lxc"
        self.container = lxc_container(container_id)

    def is_running(self):
        return self.container.running

    def timezone_needs_update(self):
        host_timezone = get_host_timezone()

        with open(os.path.join(self.root_path, 'etc', 'timezone'), 'r') as fd:
            container_timezone = fd.read().strip('\n')

        if host_timezone == container_timezone:
            return False
        else:
            return True

    def start_container(self):
        if not self.container.defined:
            raise RuntimeError("Container %s is not valid" % self.container_id)

        if not self.container.running:
            self._set_lxc_log()
            if not self.container.start():
                self._dump_lxc_log()
                raise RuntimeError("Container failed to start")
            if not self.container.wait("RUNNING", 10):
                self._dump_lxc_log()
                raise RuntimeError("Container failed to enter the RUNNING state")

        if not self.container.get_ips(timeout=30):
            self.stop_container()
            raise RuntimeError("Not able to connect to the network.")

        if self.run_in_container("mountpoint -q /tmp/.X11-unix") == 0:
            self.run_in_container("umount /tmp/.X11-unix")
        if self.run_in_container("mountpoint -q /usr/lib/locale") == 0:
            self.run_in_container("umount -l /usr/lib/locale")

    def stop_container(self):
        self.container.stop()

    def run_in_container(self, command_string):
        cmd_args = shlex.split(command_string)
        return self.container.attach_wait(lxc.attach_run_command, cmd_args)

    def update_packages(self, verbosity=1):
        if self.timezone_needs_update():
            self.run_in_container("bash -c \'echo \"{}\" >/etc/timezone\'".format(
                                  get_host_timezone()))
            self.run_in_container("rm -f /etc/localtime")
            self.run_in_container("dpkg-reconfigure -f noninteractive tzdata")

        return super().update_packages(verbosity)

    def destroy_libertine_container(self):
        if self.container.defined:
            self.container.stop()
            self.container.destroy()

    def create_libertine_container(self, password=None, multiarch=False, verbosity=1):
        if password is None:
            return False

        username = os.environ['USER']
        user_id = os.getuid()
        group_id = os.getgid()

        setup_host_environment(username)

        # Generate the default lxc default config, if it doesn't exist
        config_path = get_lxc_default_config_path()
        config_file = "%s/default.conf" % config_path

        if not os.path.exists(config_path):
            os.makedirs(config_path)

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

        utils.create_libertine_user_data_dir(self.container_id)

        if not self.container.create("download", 0,
                                     {"dist": "ubuntu",
                                      "release": self.installed_release,
                                      "arch": self.architecture}):
            print("Failed to create container")
            return False

        self.create_libertine_config()

        if verbosity == 1:
            print("starting container ...")
        try:
            self.start_container()
        except RuntimeError as e:
            print("Container failed to start: %s" % e)
            self.destroy_libertine_container()
            return False

        self.run_in_container("userdel -r ubuntu")
        self.run_in_container("useradd -u {} -p {} -G sudo {}".format(
                str(user_id), crypt.crypt(password), str(username)))

        if multiarch and self.architecture == 'amd64':
            if verbosity == 1:
                print("Adding i386 multiarch support...")
            self.run_in_container("dpkg --add-architecture i386")

        if verbosity == 1:
            print("Updating the contents of the container after creation...")
        self.update_packages(verbosity)

        for package in self.default_packages:
            if not self.install_package(package, verbosity):
                print("Failure installing %s during container creation" % package)
                self.destroy_libertine_container()
                return False

        if verbosity == 1:
            print("stopping container ...")
        self.stop_container()

        return True

    def create_libertine_config(self):
        user_id = os.getuid()
        home_entry = (
            "%s %s none bind,create=dir"
            % (utils.get_libertine_container_userdata_dir_path(self.container_id),
               home_path.strip('/'))
        )

        # Bind mount the user's home directory
        self.container.append_config_item("lxc.mount.entry", home_entry)

        xdg_user_dirs = utils.get_common_xdg_directories()

        for user_dir in xdg_user_dirs:
            xdg_user_dir_entry = (
                "%s/%s %s/%s none bind,create=dir,optional"
                % (home_path, user_dir, home_path.strip('/'), user_dir)
            )
            self.container.append_config_item("lxc.mount.entry", xdg_user_dir_entry)

        # Bind mount the user's dconf back end
        user_dconf_path = os.path.join(home_path, '.config', 'dconf')
        user_dconf_entry = (
            "%s %s none bind,create=dir,optional"
            % (user_dconf_path, user_dconf_path.strip('/'))
        )
        self.container.append_config_item("lxc.mount.entry", user_dconf_entry)

        # Setup the mounts for /run/user/$user_id
        run_user_entry = "/run/user/%s run/user/%s none rbind,optional,create=dir" % (user_id, user_id)
        self.container.append_config_item("lxc.mount.entry", "tmpfs run tmpfs rw,nodev,noexec,nosuid,size=5242880")
        self.container.append_config_item("lxc.mount.entry",
                                          "none run/user tmpfs rw,nodev,noexec,nosuid,size=104857600,mode=0755,create=dir")
        self.container.append_config_item("lxc.mount.entry", run_user_entry)

        self.container.append_config_item("lxc.include", "/usr/share/libertine/libertine-lxc.conf")

        # Dump it all to disk
        self.container.save_config()

    def launch_application(self, app_exec_line):
        libertine_lxc_mgr_sock = socket(AF_UNIX, SOCK_STREAM)
        libertine_lxc_mgr_sock.connect(utils.get_libertine_lxc_socket())

        # Tell libertine-lxc-manager that we are starting a new app
        message = "start " + self.container_id
        libertine_lxc_mgr_sock.send(message.encode())

        # Receive the reply from libertine-lxc-manager
        data = libertine_lxc_mgr_sock.recv(1024)

        if data.decode() == 'OK':
            if not self.container.wait("RUNNING", 10):
                print("Container failed to enter the RUNNING state")
                return

            if not self.container.get_ips(timeout=30):
                print("Not able to connect to the network.")
                return

        else:
            print("Failure detected from libertine-lxc-manager")
            return

        window_manager = self.container.attach(lxc.attach_run_command,
                                               utils.setup_window_manager(self.container_id))

        # Setup pulse to work inside the container
        os.environ['PULSE_SERVER'] = utils.get_libertine_lxc_pulse_socket_path()

        app_launch_cmd = "sudo -E -u " + os.environ['USER'] + " env PATH=" + os.environ['PATH']
        cmd = shlex.split(app_launch_cmd)
        self.container.attach_wait(lxc.attach_run_command,
                                   cmd + app_exec_line)

        utils.terminate_window_manager(psutil.Process(window_manager))

        # Tell libertine-lxc-manager that the app has stopped.
        message = "stop " + self.container_id
        libertine_lxc_mgr_sock.send(message.encode())

        # Receive the reply from libertine-lxc-manager (ignore it for now).
        data = libertine_lxc_mgr_sock.recv(1024)
        libertine_lxc_mgr_sock.close()

    def _set_lxc_log(self):
        self.lxc_log_file = os.path.join(tempfile.mkdtemp(), 'lxc-start.log')
        self.container.append_config_item("lxc.logfile", self.lxc_log_file)
        self.container.append_config_item("lxc.logpriority", "3")

    def _dump_lxc_log(self):
        try:
            with open(self.lxc_log_file, 'r') as fd:
                for line in fd:
                    print(line.lstrip())
        except Exception as ex:
            print("Could not open LXC log file: %s" % ex, file=sys.stderr)
