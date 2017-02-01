# Copyright 2015-2017 Canonical Ltd.
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
import time

from .Libertine import BaseContainer
from .service.manager import LIBERTINE_MANAGER_NAME, LIBERTINE_STORE_PATH
from . import utils, HostInfo


home_path = os.environ['HOME']


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

    if container.state == 'STOPPED':
        if not container.start():
            utils.get_logger().error("Container failed to start.")
            return False
    elif container.state == 'FROZEN':
        if not container.unfreeze():
            utils.get_logger().error("Container failed to unfreeze.")
            return False

    if not container.wait("RUNNING", 10):
        utils.get_logger().error("Container failed to enter the RUNNING state.")
        return False

    if not container.get_ips(timeout=30):
        lxc_stop(container)
        utils.get_logger().error("Not able to connect to the network.")
        return False

    return True


def lxc_stop(container, freeze_on_stop=False):
    if container.state == 'STOPPED' or not container.running:
        return

    if freeze_on_stop:
        container.freeze()
    else:
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

    def __init__(self, container_id, config):
        super().__init__(container_id, 'lxc', config)
        self.container = lxc_container(container_id)
        self.lxc_manager_interface = None
        self.window_manager = None
        self.host_info = HostInfo.HostInfo()
        self._freeze_on_stop = config.get_freeze_on_stop(self.container_id)

        if utils.set_session_dbus_env_var():
            try:
                bus = dbus.SessionBus()
                self.lxc_manager_interface = bus.get_object(LIBERTINE_MANAGER_NAME, LIBERTINE_STORE_PATH)
            except dbus.exceptions.DBusException:
                pass

    def _setup_pulse(self):
        pulse_socket_path = os.path.join(utils.get_libertine_runtime_dir(), 'pulse_socket')

        os.environ['PULSE_SERVER'] = pulse_socket_path

        lsof_cmd = 'lsof -n %s' % pulse_socket_path
        args = shlex.split(lsof_cmd)
        lsof = subprocess.Popen(args, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        lsof.wait()

        if not os.path.exists(pulse_socket_path) or lsof.returncode == 1:
            pactl_cmd = (
                'pactl load-module module-native-protocol-unix auth-anonymous=1 socket=%s'
                % pulse_socket_path)
            args = shlex.split(pactl_cmd)
            subprocess.Popen(args).wait()

    def _dynamic_bind_mounts(self):
        self._config.refresh_database()
        mounts = self._sanitize_bind_mounts(utils.get_common_xdg_user_directories() + \
                                            self._config.get_container_bind_mounts(self.container_id))

        data_dir = utils.get_libertine_container_home_dir(self.container_id)
        for user_dir in utils.generate_binding_directories(mounts, home_path):
            if os.path.isabs(user_dir[1]):
                path = user_dir[1].strip('/')
                fullpath = os.path.join(utils.get_libertine_container_rootfs_path(self.container_id), path)
            else:
                path = "{}/{}".format(home_path.strip('/'), user_dir[1])
                fullpath = os.path.join(data_dir, user_dir[1])

            os.makedirs(fullpath, exist_ok=True)

            utils.get_logger().debug("Mounting {}:{} in container {}".format(user_dir[0], path, self.container_id))
            xdg_user_dir_entry = (
                "%s %s none bind,create=dir,optional"
                % (user_dir[0], path)
            )
            self.container.append_config_item("lxc.mount.entry", xdg_user_dir_entry)

    def _sanitize_bind_mounts(self, mounts):
        return [mount.replace(" ", "\\040") for mount in mounts]

    def timezone_needs_update(self):
        with open(os.path.join(self.root_path, 'etc', 'timezone'), 'r') as fd:
            return fd.read().strip('\n') != self.host_info.get_host_timezone()

    def start_container(self):
        if self.lxc_manager_interface:
            retries = 0
            while not self.lxc_manager_interface.container_operation_start(self.container_id):
                retries += 1
                if retries > 5:
                    return False
                time.sleep(.5)
             
        if self.container.state == 'RUNNING':
            return True

        if self.container.state == 'STOPPED':
            self._dynamic_bind_mounts()
            self._setup_pulse()

        if not lxc_start(self.container):
            _dump_lxc_log(result.logfile)
            return False

        return True

    def stop_container(self):
        if self.lxc_manager_interface:
            stop = self.lxc_manager_interface.container_operation_finished(self.container_id)
            if stop: 
                lxc_stop(self.container, self._freeze_on_stop)
                self.lxc_manager_interface.container_stopped(self.container_id)
        else:
            lxc_stop(self.container, self._freeze_on_stop)

    def run_in_container(self, command_string):
        cmd_args = shlex.split(command_string)
        return self.container.attach_wait(lxc.attach_run_command, cmd_args)

    def update_packages(self, update_locale=False):
        if self.timezone_needs_update():
            self.run_in_container("bash -c \'echo \"{}\" >/etc/timezone\'".format(
                                  self.host_info.get_host_timezone()))
            self.run_in_container("rm -f /etc/localtime")
            self.run_in_container("dpkg-reconfigure -f noninteractive tzdata")

        return super().update_packages(update_locale)

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

        self._create_libertine_user_data_dir()

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
        if not self.start_container():
            self.destroy_libertine_container()
            return False

        self.update_locale()

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

        super().create_libertine_container()

        utils.get_logger().info("stopping container ...")
        self.stop_container()

        return True

    def create_libertine_config(self):
        user_id = os.getuid()
        home_entry = (
            "%s %s none bind,create=dir"
            % (utils.get_libertine_container_home_dir(self.container_id),
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

        if not self.start_container():
            self.lxc_manager_interface.container_stopped(self.container_id)
            return

        self.window_manager = self.container.attach(lxc.attach_run_command,
                                                    self.setup_window_manager())

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

        self.stop_container()
