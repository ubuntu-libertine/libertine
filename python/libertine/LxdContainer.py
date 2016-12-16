# Copyright 2016 Canonical Ltd.
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
import os
import psutil
import pylxd
import shlex
import subprocess
import time
from libertine import Libertine, utils, HostInfo


def _get_devices_map():
    devices = {
        '/dev/tty0':   {'path': '/dev/tty0', 'type': 'unix-char'},
        '/dev/tty7':   {'path': '/dev/tty7', 'type': 'unix-char'},
        '/dev/tty8':   {'path': '/dev/tty8', 'type': 'unix-char'},
        '/dev/fb0':    {'path': '/dev/fb0', 'type': 'unix-char'},
        'x11-socket':  {'source': '/tmp/.X11-unix', 'path': '/tmp/.X11-unix', 'type': 'disk', 'optional': 'true'},
    }

    if os.path.exists('/dev/video0'):
        devices['/dev/video0'] = {'path': '/dev/video0', 'type': 'unix-char'}

    # every regular file in /dev/snd
    for f in ['/dev/snd/{}'.format(f) for f in os.listdir('/dev/snd') if not os.path.isdir('/dev/snd/{}'.format(f))]:
        devices[f] = {'path': f, 'type': 'unix-char'}

    # every regular file in /dev/dri
    for f in ['/dev/dri/{}'.format(f) for f in os.listdir('/dev/dri') if not os.path.isdir('/dev/dri/{}'.format(f))]:
        devices[f] = {'path': f, 'type': 'unix-char'}

    # Some devices require special mappings for snap
    if utils.is_snap_environment():
        devices['x11-socket']['source'] = '/var/lib/snapd/hostfs/tmp/.X11-unix'

    return devices

def _readlink(source):
    while os.path.islink(source):
        new_source = os.readlink(source)
        if not os.path.isabs(new_source):
            new_source = os.path.join(os.path.dirname(source), new_source)
        source = new_source

    return source

def _setup_lxd():
    import pexpect
    child = pexpect.spawnu('sudo libertine-lxd-setup {}'.format(os.environ['USER']), env={'TERM': 'dumb'})

    while True:
        index = child.expect(['.+\[default=.+\].*', pexpect.EOF, pexpect.TIMEOUT,
                              # The following are required for lxd=2.0.x
                              '.+\[yes/no\].*',
                              '.+\(e.g. (?P<example>[a-z0-9\.:]+)\).+'])
        if index == 0:
            child.sendline()
        elif index == 1:
            return True
        elif index == 2:
            return False
        elif index == 3:
            child.sendline('yes')
        elif index == 4:
            child.sendline(child.match.group('example'))

        if child.exitstatus is not None:
            return child.exitstatus == 0


def _setup_bind_mount_service(container, uid, username):
    utils.get_logger().info("Creating systemd mount override service")
    service = '''
[Unit]
Description=Fix system mounts for libertine

[Service]
ExecStart=/usr/bin/libertine-lxd-mount-update

[Install]
WantedBy=multi-user.target
'''[1:-1]
    container.files.put('/etc/systemd/system/libertine-lxd-mount-update.service', service.encode('utf-8'))

    utils.get_logger().info("Creating mount update shell script")
    script = '''
#!/bin/sh

mkdir -p /run/user/{uid}
chown {username}:{username} /run/user/{uid}
mount -o bind /var/tmp/run/user/{uid} /run/user/{uid}

chgrp audio /dev/snd/*
chgrp video /dev/dri/*
[ -n /dev/video0 ] && chgrp video /dev/video0
'''[1:-1]
    container.files.put('/usr/bin/libertine-lxd-mount-update', script.format(uid=uid, username=username).encode('utf-8'))
    container.execute(shlex.split('chmod +x /usr/bin/libertine-lxd-mount-update'))

    utils.get_logger().info("Enabling systemd mount update service")
    container.execute(shlex.split('systemctl enable libertine-lxd-mount-update.service'))


class LibertineLXD(Libertine.BaseContainer):
    def __init__(self, name, config):
        super().__init__(name)
        self._id = name
        self._config = config
        self._host_info = HostInfo.HostInfo()
        self._container = None
        self._matchbox_pid = None

        if not _setup_lxd():
            raise Exception("Failed to setup lxd.")

        self._client = pylxd.Client()
        self._window_manager = None
        self.root_path = '{}/containers/{}/rootfs'.format(os.getenv('LXD_DIR', '/var/lib/lxd'), name)

    def _update_libertine_profile(self):
        try:
            profile = self._client.profiles.get('libertine')

            utils.get_logger().info('Updating existing lxd profile.')
            profile.devices = _get_devices_map()
            profile.config['raw.idmap'] = 'both 1000 1000'

            try:
                profile.save()
            except pylxd.exceptions.LXDAPIException as e:
                utils.get_logger().warning('Saving libertine lxd profile raised: {}'.format(str(e)))
                # This is most likely the result of an older container currently
                # running and/or containing a conflicting device entry
        except pylxd.exceptions.LXDAPIException:
            utils.get_logger().info('Creating libertine lxd profile.')
            self._client.profiles.create('libertine', config={'raw.idmap': 'both 1000 1000'}, devices=_get_devices_map())

    def create_libertine_container(self, password=None, multiarch=False, verbosity=1):
        if self._try_get_container():
            utils.get_logger().error("Container already exists")
            return False

        self._update_libertine_profile()

        utils.get_logger().info("Creating container '%s' with distro '%s'" % (self._id, self.installed_release))
        self._container = self._client.containers.create({'name': self._id,
                                                          'profiles': ['default', 'libertine'],
                                                          'source': {"type": "image",
                                                                     "protocol": "simplestreams",
                                                                     "server": "https://cloud-images.ubuntu.com/daily",
                                                                     "alias": self.installed_release}},
                                                          wait=True)

        if not self.start_container():
            utils.get_logger().error("Failed to start container '{}'".format(self._id))
            self.destroy_libertine_container()
            return False

        username = os.environ['USER']
        uid = str(os.getuid())
        self.run_in_container("userdel -r ubuntu")
        self.run_in_container("useradd -u {} -U -p {} -G sudo,audio,video {}".format(
            uid, crypt.crypt(''), username))
        self.run_in_container("mkdir -p /home/{}".format(username))
        self.run_in_container("chown {0}:{0} /home/{0}".format(username))

        _setup_bind_mount_service(self._container, uid, username)

        if multiarch and self.architecture == 'amd64':
            utils.get_logger().info("Adding i386 multiarch support to container '{}'".format(self._id))
            self.run_in_container("dpkg --add-architecture i386")

        self.update_packages()

        for package in self.default_packages:
            utils.get_logger().info("Installing package '%s' in container '%s'" % (package, self._id))
            if not self.install_package(package, verbosity=1, no_dialog=True, update_cache=False):
                utils.get_logger().error("Failure installing '%s' during container creation" % package)
                self.destroy_libertine_container()
                return False

        return True

    def _wait_for_network(self):
        for retries in range(0, 10):
            out, err = self._container.execute(shlex.split('ping -c 1 ubuntu.com'))
            if out:
                utils.get_logger().info("Network connection active")
                return True
            time.sleep(1)
        return False

    def update_packages(self, verbosity=1):
        if not self._timezone_in_sync():
            utils.get_logger().info("Re-syncing timezones")
            self.run_in_container("bash -c 'echo \"%s\" > /etc/timezone'" % self._host_info.get_host_timezone())
            self.run_in_container("rm -f /etc/localtime")
            self.run_in_container("dpkg-reconfigure -f noninteractive tzdata")

        return super().update_packages()

    def destroy_libertine_container(self):
        if not self._try_get_container():
            utils.get_logger().error("No such container '%s'" % self._id)
            return False

        self.stop_container(wait=True)
        self._container.delete()
        return True

    def _timezone_in_sync(self):
        proc = subprocess.Popen(self._lxc_args('cat /etc/timezone'), stdout=subprocess.PIPE)
        out, err = proc.communicate()
        return out.decode('UTF-8').strip('\n') == self._host_info.get_host_timezone()

    def _lxc_args(self, command, environ={}):
        env_as_args = ' '
        for k, v in environ.items():
            env_as_args += '--env {}="{}" '.format(k, v)

        return shlex.split('lxc exec {}{}-- {}'.format(self._id,
                                                       env_as_args,
                                                       command))

    def run_in_container(self, command):
        proc = subprocess.Popen(self._lxc_args(command))
        return proc.wait()

    def start_container(self):
        if not self._try_get_container():
            return False

        if self._container.status == 'Running':
            return True

        self._container.start(wait=True)

        # Connect to network
        if not self._wait_for_network():
            utils.get_logger().error("Network unavailable in container '{}'".format(self._id))
            return False

        self._container.sync(rollback=True) # required for pylxd=2.0.x

        return self._container.status == 'Running'

    def stop_container(self, wait=False):
        if not self._try_get_container():
            return False

        if self._container.status == 'Stopped':
            return True

        self._container.stop(wait=wait)

        return not wait or self._container.status == 'Stopped'

    def _update_bind_mounts(self):
        home_path = os.environ['HOME']

        self._container.devices.clear()
        self._container.devices['root'] = {'type': 'disk', 'path': '/'}

        if os.path.exists(os.path.join(home_path, '.config', 'dconf')):
            self._container.devices['dconf'] = {
                'type': 'disk',
                'source': os.path.join(home_path, '.config', 'dconf'),
                'path': os.path.join(home_path, '.config', 'dconf')
            }

        run_user = '/run/user/{}'.format(os.getuid())
        self._container.devices[run_user] = {'source': run_user, 'path': '/var/tmp{}'.format(run_user), 'type': 'disk'}

        mounts = utils.get_common_xdg_user_directories() + \
                 self._config.get_container_bind_mounts(self._id)
        for user_dir in utils.generate_binding_directories(mounts, home_path):
            if not os.path.exists(user_dir[0]):
                utils.get_logger().warning('Bind-mount path \'{}\' does not exist.'.format(user_dir[0]))
                continue

            self._container.devices[user_dir[1]] = {
                    'source': _readlink(user_dir[0]),
                    'path': os.path.join(home_path, user_dir[1]),
                    'type': 'disk'
            }

        try:
            self._container.save(wait=True)
        except pylxd.exceptions.LXDAPIException as e:
            utils.get_logger().warning('Saving bind mounts for container \'{}\' raised: {}'.format(self._id, str(e)))
            # This is most likely the result of the container currently running

    def _get_matchbox_pids(self):
        p = subprocess.Popen(self._lxc_args('pgrep matchbox'), stdout=subprocess.PIPE)
        out, err = p.communicate()
        return out.decode('utf-8').split('\n')

    # FIXME: Remove once window management logic has been moved to the host
    def _start_window_manager(self, args):
        args.extend(utils.setup_window_manager(self._id))

        if 'matchbox-window-manager' in args:
            pids = self._get_matchbox_pids()

        self._window_manager = psutil.Popen(args)

        time.sleep(.25) # Give matchbox a moment to start in the container
        if self._window_manager.poll() is not None:
            utils.get_logger().warning("Window manager terminated prematurely with exit code '{}'".format(
                                       self._window_manager.returncode))
            self._window_manager = None
        elif 'matchbox-window-manager' in args:
            after_pids = self._get_matchbox_pids()
            if len(after_pids) > len(pids):
                self._matchbox_pid = (set(after_pids) - set(pids)).pop()

    def start_application(self, app_exec_line, environ):
        if not self._try_get_container():
            utils.get_logger().error("Could not get container '{}'".format(self._id))
            return None

        self._update_libertine_profile()
        self._update_bind_mounts()
        self.start_container()

        args = self._lxc_args("sudo -E -u {} env PATH={}".format(os.environ['USER'], environ['PATH']), environ)

        self._start_window_manager(args.copy())

        args.extend(app_exec_line)
        return psutil.Popen(args)

    def finish_application(self, app):
        if self._window_manager is not None:
            utils.terminate_window_manager(self._window_manager)
            self._window_manager = None

            # This is a workaround for an issue on xenial where the process
            # running the window manager is not killed with the application
            if self._matchbox_pid is not None:
                utils.get_logger().debug("Manually killing matchbox-window-manager")
                self.run_in_container("kill -9 {}".format(self._matchbox_pid))
                self._matchbox_pid = None

        app.wait()

    def copy_file_to_container(self, source, dest):
        with open(source, 'rb') as f:
            return self._container.files.put(dest, f.read())

    def delete_file_in_container(self, path):
        return self.run_in_container('rm {}'.format(path))

    def _try_get_container(self):
        if self._container is None:
            try:
                self._container = self._client.containers.get(self._id)
            except pylxd.exceptions.LXDAPIException:
                self._container = None
                return False

        return True
