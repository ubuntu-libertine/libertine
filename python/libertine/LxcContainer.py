# Copyright 2015-2016 Canonical Ltd.
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

import contextlib
import crypt
import dbus
import lxc
import os
import psutil
import shlex
import subprocess
import sys
import tempfile

from .lifecycle import LifecycleResult
from .Libertine import BaseContainer
from . import utils, HostInfo


home_path = os.environ['HOME']

LIBERTINE_LXC_MANAGER_NAME = "com.canonical.libertine.LxcManager"
LIBERTINE_LXC_MANAGER_PATH = "/LxcManager"


def _check_lxc_net_entry(entry):
    lxc_net_file = open('/etc/lxc/lxc-usernet')
    found = False

    for line in lxc_net_file:
        if entry in line:
            found = True
            break

    return found


def _setup_host_environment(username):
    lxc_net_entry = "%s veth lxcbr0 10" % str(username)

    if not _check_lxc_net_entry(lxc_net_entry):
        subprocess.Popen(["sudo", "libertine-lxc-setup", str(username)]).wait()


def _get_lxc_default_config_path():
    return os.path.join(home_path, '.config', 'lxc')


def get_lxc_manager_dbus_name():
    return LIBERTINE_LXC_MANAGER_NAME


def get_lxc_manager_dbus_path():
    return LIBERTINE_LXC_MANAGER_PATH


def lxc_container(container_id):
    config_path = utils.get_libertine_containers_dir_path()
    if not os.path.exists(config_path):
        os.makedirs(config_path)

    container = lxc.Container(container_id, config_path)

    return container


def _dump_lxc_log(logfile):
    if os.path.exists(logfile):
        try:
            with open(logfile, 'r') as fd:
                for line in fd:
                    print(line.lstrip())
        except Exception as ex:
            utils.get_logger().error("Could not open LXC log file: %s" % ex)


def get_logfile(container):
    try:
        logfile = container.get_config_item('lxc.logfile')
    except:
        logfile = None

    if not container.running or logfile is None or not os.path.exists(logfile):
        logfile = os.path.join(tempfile.mkdtemp(), 'lxc-start.log')
        container.append_config_item("lxc.logfile", logfile)
        container.append_config_item("lxc.logpriority", "3")

    return logfile

def lxc_start(container):
    lxc_log_file = get_logfile(container)

    if not container.start():
        return LifecycleResult("Container failed to start.")

    if not container.wait("RUNNING", 10):
        return LifecycleResult("Container failed to enter the RUNNING state.")

    if not container.get_ips(timeout=30):
        lxc_stop(container)
        return LifecycleResult("Not able to connect to the network.")

    return LifecycleResult()


def lxc_stop(container):
    if container.running:
        container.stop()


class EnvLxcSettings(contextlib.ExitStack):
    """
    Helper object providing a way to set the proxies for testing

    When running smoke tests on Jenkins, LXC create operations need the proxies
    set, but subsequent apt operations cannot have the proxies set.  This will
    set the proxies when called and unset the proxies when the context is
    destroyed.
    """
    def __init__(self):
        super().__init__()
        self.set_proxy_env()
        self.callback(lambda: self.del_proxy_env())

    def set_proxy_env(self):
        if 'LIBERTINE_JENKAAS_TESTING' in os.environ:
            os.environ['http_proxy'] = 'http://squid.internal:3128'
            os.environ['https_proxy'] = 'https://squid.internal:3128'

    def del_proxy_env(self):
        if 'LIBERTINE_JENKAAS_TESTING' in os.environ:
            del os.environ['http_proxy']
            del os.environ['https_proxy']


class LibertineLXC(BaseContainer):
    """
    A concrete container type implemented using an LXC container.
    """

    def __init__(self, container_id):
        super().__init__(container_id)
        self.container_type = "lxc"
        self.container = lxc_container(container_id)
        self.lxc_manager_interface = None
        self.window_manager = None
        self.host_info = HostInfo.HostInfo()

        utils.set_session_dbus_env_var()

        try:
            bus = dbus.SessionBus()
            self.lxc_manager_interface = bus.get_object(get_lxc_manager_dbus_name(), get_lxc_manager_dbus_path())
        except dbus.exceptions.DBusException:
            pass

    def timezone_needs_update(self):
        with open(os.path.join(self.root_path, 'etc', 'timezone'), 'r') as fd:
            return fd.read().strip('\n') != self.host_info.get_host_timezone()

    def start_container(self):
        if self.lxc_manager_interface:
            result = LifecycleResult.from_dict(self.lxc_manager_interface.operation_start(self.container_id))
        else:
            result = lxc_start(self.container)

        if not result.success:
            _dump_lxc_log(result.logfile)
            raise RuntimeError(result.error)

        if self.run_in_container("mountpoint -q /tmp/.X11-unix") == 0:
            self.run_in_container("umount /tmp/.X11-unix")

    def stop_container(self):
        if self.lxc_manager_interface:
            self.lxc_manager_interface.operation_stop(self.container_id)
        else:
            lxc_stop(self.container)

    def run_in_container(self, command_string):
        cmd_args = shlex.split(command_string)
        return self.container.attach_wait(lxc.attach_run_command, cmd_args)

    def update_packages(self):
        if self.timezone_needs_update():
            self.run_in_container("bash -c \'echo \"{}\" >/etc/timezone\'".format(
                                  self.host_info.get_host_timezone()))
            self.run_in_container("rm -f /etc/localtime")
            self.run_in_container("dpkg-reconfigure -f noninteractive tzdata")

        return super().update_packages()

    def destroy_libertine_container(self):
        if not self.container.defined:
            return False

        self.container.stop()
        self.container.destroy()
        return True

    def create_libertine_container(self, password=None, multiarch=False):
        if password is None:
            return False

        username = os.environ['USER']
        user_id = os.getuid()
        group_id = os.getgid()

        _setup_host_environment(username)

        # Generate the default lxc default config, if it doesn't exist
        config_path = _get_lxc_default_config_path()
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

        self.container.load_config(config_file)

        utils.create_libertine_user_data_dir(self.container_id)

        with EnvLxcSettings():
            lxc_logfile = get_logfile(self.container)
            if not self.container.create("download", 0,
                                         {"dist": "ubuntu",
                                          "release": self.installed_release,
                                          "arch": self.architecture}):
                utils.get_logger().error("Failed to create container")
                _dump_lxc_log(lxc_logfile)
                return False

        self.create_libertine_config()

        utils.get_logger().info("starting container ...")
        try:
            self.start_container()
        except RuntimeError as e:
            utils.get_logger().error("Container failed to start: %s" % e)
            self.destroy_libertine_container()
            return False

        self.run_in_container("userdel -r ubuntu")
        self.run_in_container("useradd -u {} -p {} -G sudo {}".format(
                str(user_id), crypt.crypt(password), str(username)))

        if multiarch and self.architecture == 'amd64':
            utils.get_logger().info("Adding i386 multiarch support...")
            self.run_in_container("dpkg --add-architecture i386")

        utils.get_logger().info("Updating the contents of the container after creation...")
        self.update_packages()

        for package in self.default_packages:
            if not self.install_package(package, update_cache=False):
                utils.get_logger().error("Failure installing %s during container creation" % package)
                self.destroy_libertine_container()
                return False

        utils.get_logger().info("stopping container ...")
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

    def start_application(self, app_exec_line, environ):
        if self.lxc_manager_interface == None:
            utils.get_logger().error("No interface to libertine-lxc-manager.  Failing application launch.")
            return

        os.environ.clear()
        os.environ.update(environ)

        result = LifecycleResult.from_dict(self.lxc_manager_interface.app_start(self.container_id))

        if not result.success:
            _dump_lxc_log(get_logfile(self.container))
            utils.get_logger().error("%s" % result.error)
            return

        self.window_manager = self.container.attach(lxc.attach_run_command,
                                                    utils.setup_window_manager(self.container_id))

        # Setup pulse to work inside the container
        os.environ['PULSE_SERVER'] = utils.get_libertine_lxc_pulse_socket_path()

        app_launch_cmd = "sudo -E -u " + os.environ['USER'] + " env PATH=" + os.environ['PATH']
        cmd = shlex.split(app_launch_cmd)
        app = self.container.attach(lxc.attach_run_command,
                                    cmd + app_exec_line)
        return psutil.Process(app)

    def finish_application(self, app):
        os.waitpid(app.pid, 0)

        utils.terminate_window_manager(psutil.Process(self.window_manager))

        # Tell libertine-lxc-manager that the app has stopped.
        self.lxc_manager_interface.app_stop(self.container_id)
