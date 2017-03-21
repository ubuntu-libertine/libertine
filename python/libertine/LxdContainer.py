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

import contextlib
import crypt
import os
import psutil
import pylxd
import shlex
import shutil
import subprocess
import time

from . import Libertine, utils, HostInfo


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
    if utils.is_snap_environment():
        utils.get_logger().warning("Running in snap environment, skipping automatic lxd setup.")
        return True

    utils.get_logger().info("Running LXD setup.")
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
    utils.get_logger().info("Creating mount update shell script")
    script = '''
#!/bin/sh

mkdir -p /run/user/{uid}
chown {username}:{username} /run/user/{uid}
chmod 755 /run/user/{uid}
mount -o bind /var/tmp/run/user/{uid} /run/user/{uid}

chgrp audio /dev/snd/*
chgrp video /dev/dri/*
[ -n /dev/video0 ] && chgrp video /dev/video0
'''[1:-1]
    container.files.put('/usr/bin/libertine-lxd-mount-update', script.format(uid=uid, username=username).encode('utf-8'))
    subprocess.Popen(shlex.split("lxc exec {} -- chmod 755 /usr/bin/libertine-lxd-mount-update".format(container.name)))


def lxd_container(client, container_id):
    try:
        return client.containers.get(container_id)
    except pylxd.exceptions.LXDAPIException:
        return None


def _wait_for_network(container):
    for retries in range(0, 10):
        ping = subprocess.Popen(shlex.split("lxc exec {} -- ping -c 1 ubuntu.com".format(container.name)),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = ping.communicate()
        if out:
            utils.get_logger().info("Network connection active")
            return True
        time.sleep(1)
    return False


def lxd_start(container):
    if container.status == 'Stopped':
        container.start(wait=True)
    elif container.status == 'Frozen':
        container.unfreeze(wait=True)

    container.sync(rollback=True) # required for pylxd=2.0.x

    if container.status != 'Running':
        utils.get_logger().error("Container {} failed to start".format(container.name))
        return False

    return True


def lxd_stop(container, wait=True, freeze_on_stop=False):
    if container.status == 'Stopped':
        return True

    if freeze_on_stop:
        container.freeze(wait=wait)
    else:
        container.stop(wait=wait)

    container.sync(rollback=True) # required for pylxd=2.0.x

    if wait:
        if freeze_on_stop and container.status != 'Frozen':
            utils.get_logger().error("Container {} failed to freeze".format(container.name))
            return False
        elif not freeze_on_stop and container.status != 'Stopped':
            utils.get_logger().error("Container {} failed to stop".format(container.name))
            return False

    return True


def _lxd_save(entity, error, wait=True):
    try:
        entity.save(wait=wait)
    except pylxd.exceptions.LXDAPIException as e:
        utils.get_logger().warning('{} {}'.format(error, str(e)))


_CONTAINER_DATA_DIRS = ["/usr/share/applications", "/usr/share/icons", "/usr/local/share/applications", "/usr/share/pixmaps"]


def _sync_application_dirs_to_host(container):
    host_root = utils.get_libertine_container_rootfs_path(container.name)
    for container_path in _CONTAINER_DATA_DIRS:
        utils.get_logger().info("Syncing applications directory: {}".format(container_path))
        os.makedirs(os.path.join(host_root, container_path.lstrip("/")), exist_ok=True)

        # find a list of files within the container
        find = subprocess.Popen(shlex.split("lxc exec {} -- find {} -type f".format(container.name, container_path)), stdout=subprocess.PIPE)
        stdout, stderr = find.communicate()

        if find.returncode != 0:
            return

        for filepath in stdout.decode('utf-8').strip().split('\n'):
            if not filepath:
                continue

            host_path = os.path.join(host_root, filepath.lstrip("/"))
            if not os.path.exists(host_path):
                utils.get_logger().info("Syncing file: {}:{}".format(filepath, host_path))
                os.makedirs(os.path.dirname(host_path), exist_ok=True)
                with open(host_path, 'wb') as f:
                    f.write(container.files.get(filepath))


def _lxc_args(container_id, command, environ={}):
    env_as_args = ' '
    for k, v in environ.items():
        env_as_args += '--env {}="{}" '.format(k, v)
    return shlex.split('lxc exec {}{}-- {}'.format(container_id,
                                                   env_as_args,
                                                   command))


def _add_local_files_for_ual(container):
    root_path = utils.get_libertine_container_rootfs_path(container.name)
    find = subprocess.Popen(shlex.split("find %s -type l -! -exec test -e {} \; -print" % os.path.join(root_path, 'usr')),
                            stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    find_stdout, stderr = find.communicate()
    if find.returncode != 0:
        utils.get_logger().warning(stderr.decode('utf-8').strip())
        return

    broken_host_links = [link for link in find_stdout.decode('utf-8').strip().split('\n') if link]
    if len(broken_host_links) == 0:
        return # no broken links means no reason to continue

    broken_container_links = [link.replace(root_path, '') for link in broken_host_links]
    links = subprocess.Popen(_lxc_args(container.name, 'bash -c "echo -n {} | xargs -d , -n 1 -I % bash -c \'readlink -e  % || echo\'"'.format(','.join(broken_container_links))),
                             stdout=subprocess.PIPE)
    links_stdout, stderr = links.communicate()

    container_link_endpoints = [link.strip() for link in links_stdout.decode('utf-8').split('\n')[:-1]]

    if len(broken_host_links) != len(container_link_endpoints):
        utils.get_logger().warning("Link mismatch while trying to fix symbolic links.")
        return

    for i in range(0, len(broken_host_links)):
        if not container_link_endpoints[i] or broken_container_links[i] == container_link_endpoints[i] \
           or container_link_endpoints[i].startswith(root_path):
            continue # link wasn't found

        host_linkpath = os.path.join(root_path, container_link_endpoints[i].lstrip('/'))
        if not os.path.exists(host_linkpath):
            os.makedirs(os.path.dirname(host_linkpath), exist_ok=True)
            with open(host_linkpath, 'wb') as f:
                try:
                    f.write(container.files.get(container_link_endpoints[i]))
                except pylxd.exceptions.NotFound as e:
                    utils.get_logger().warning("Error during symlink copy of {}: {}".format(container_link_endpoints[i], str(e)))
                    continue

        subprocess.Popen(_lxc_args(container.name, "ln -sf --relative {} {}".format(
                                   container_link_endpoints[i],
                                   broken_host_links[i].replace(root_path, '')))).wait()


def _remove_local_files_for_ual(container):
    root_path = utils.get_libertine_container_rootfs_path(container.name)
    find = subprocess.Popen(shlex.split("find {} -type f".format(root_path)), stdout=subprocess.PIPE)
    find_stdout, stderr = find.communicate()
    if find.returncode != 0:
        utils.get_logger().warning("Finding local files to remove failed.")
        return

    existing_files = [f.replace(root_path, '') for f in find_stdout.decode('UTF-8').strip().split('\n') if f]
    for d in  _CONTAINER_DATA_DIRS:
        existing_files = [f for f in existing_files if not f.startswith(d)]
    if len(existing_files) == 0:
        return

    missing_files = subprocess.Popen(_lxc_args(container.name,
                                               'bash -c "echo -n {} | xargs -d , -I % bash -c \'test -e % || echo %\'"'.format(','.join(existing_files))), stdout=subprocess.PIPE)
    remove_stdout, stderr = missing_files.communicate()
    if missing_files.returncode != 0:
        utils.get_logger().warning("Checking for missing files failed.")
        return

    for f in [os.path.join(root_path, f.lstrip('/')) for f in remove_stdout.decode('UTF-8').strip().split('\n') if f]:
        try:
            os.remove(f)
        except PermissionError as e:
            utils.get_logger().warning("Error while trying to remove local file {}: {}".format(f, str(e)))

    # now remove any dangling directories
    empty_dirs = subprocess.Popen(shlex.split("find {} -depth -type d -empty".format(root_path)), stdout=subprocess.PIPE)
    empty_out, stderr = empty_dirs.communicate()
    if empty_dirs.returncode != 0:
        utils.get_logger().warning("Looking for local empty directories failed.")
        return

    deleteable_dirs = [d for d in empty_out.decode('UTF-8').strip().split('\n') if d]
    for d in _CONTAINER_DATA_DIRS:
        deleteable_dirs = [dd for dd in deleteable_dirs if not dd.startswith(os.path.join(root_path, d.lstrip('/')))]

    for d in deleteable_dirs:
        subprocess.Popen(shlex.split("rmdir -p --ignore-fail-on-non-empty {}".format(d))).wait()


def update_bind_mounts(container, config, home_path):
    userdata_dir = utils.get_libertine_container_home_dir(container.name)

    old_root = container.devices.get('root')
    container.devices.clear()
    if old_root:
        container.devices['root'] = old_root

    container.devices['home'] = {'type': 'disk', 'path': home_path, 'source': userdata_dir}

    # applications and icons directories
    rootfs_path = utils.get_libertine_container_rootfs_path(container.name)
    for data_dir in _CONTAINER_DATA_DIRS:
        host_path = os.path.join(rootfs_path, data_dir.lstrip('/'))
        os.makedirs(host_path, exist_ok=True)
        container.devices[data_dir] = {'type': 'disk', 'path': data_dir, 'source': host_path}

    if os.path.exists(os.path.join(home_path, '.config', 'dconf')):
        container.devices['dconf'] = {
            'type': 'disk',
            'source': os.path.join(home_path, '.config', 'dconf'),
            'path': os.path.join(home_path, '.config', 'dconf')
        }

    run_user = '/run/user/{}'.format(os.getuid())
    container.devices[run_user] = {'source': run_user, 'path': '/var/tmp{}'.format(run_user), 'type': 'disk'}

    mounts = config.get_container_bind_mounts(container.name)
    if utils.is_snap_environment():
        mounts += [os.path.join(home_path, d) for d in ["Documents", "Downloads", "Music", "Videos", "Pictures"]]
    else:
        mounts += utils.get_common_xdg_user_directories()

    for user_dir in utils.generate_binding_directories(mounts, home_path.rstrip('/')):
        if not os.path.exists(user_dir[0]):
            utils.get_logger().warning('Bind-mount path \'{}\' does not exist.'.format(user_dir[0]))
            continue

        if os.path.isabs(user_dir[1]):
            path = user_dir[1]
        else:
            path = os.path.join(home_path, user_dir[1])
            hostpath = os.path.join(userdata_dir, user_dir[1])
            os.makedirs(hostpath, exist_ok=True)

        utils.get_logger().debug("Mounting {}:{} in container {}".format(user_dir[0], path, container.name))

        container.devices[user_dir[1] or user_dir[0]] = {
                'source': _readlink(user_dir[0]),
                'path': path,
                'optional': 'true',
                'type': 'disk'
        }

    _lxd_save(container, 'Saving bind mounts for container \'{}\' raised:'.format(container.name))


def _setup_etc_hosts(container):
    self_host = '127.0.1.1 %s' % container.name
    hosts = container.files.get("/etc/hosts")

    lines = [line for line in hosts.decode('utf-8').split('\n')]
    found = [line for line in lines if line == self_host]
    if len(found) == 0:
        lines.insert(1, self_host)

    container.files.put("/etc/hosts", '\n'.join(lines).encode('utf-8'))


def update_libertine_profile(client):
    try:
        profile = client.profiles.get('libertine')

        utils.get_logger().info('Updating existing lxd profile.')
        profile.devices = _get_devices_map()
        profile.config['raw.idmap'] = 'both 1000 1000'

        _lxd_save(profile, 'Saving libertine lxd profile raised:')
    except pylxd.exceptions.LXDAPIException:
        utils.get_logger().info('Creating libertine lxd profile.')
        client.profiles.create('libertine', config={'raw.idmap': 'both 1000 1000'}, devices=_get_devices_map())


def env_home_path():
    if utils.is_snap_environment():
        return '/home/{}'.format(os.environ['USER'])
    return os.environ['HOME']


class LibertineLXD(Libertine.BaseContainer):
    def __init__(self, name, config, service):
        super().__init__(name, 'lxd', config, service)
        self._host_info = HostInfo.HostInfo()
        self._container = None
        self._freeze_on_stop = config.get_freeze_on_stop(self.container_id)

        if not _setup_lxd():
            raise Exception("Failed to setup lxd.")

        self._lxd_client = pylxd.Client()

    def create_libertine_container(self, password=None, multiarch=False):
        if self._try_get_container():
            utils.get_logger().error("Container already exists")
            return False

        update_libertine_profile(self._lxd_client)

        utils.get_logger().info("Creating container '%s' with distro '%s'" % (self.container_id, self.installed_release))
        create = subprocess.Popen(shlex.split('lxc launch ubuntu-daily:{distro} {id} --profile '
                                              'default --profile libertine'.format(
                                              distro=self.installed_release, id=self.container_id)))
        if create.wait() is not 0:
            utils.get_logger().error("Creating container '{}' failed with code '{}'".format(self.container_id, create.returncode))
            return False

        self._try_get_container()
        _sync_application_dirs_to_host(self._container)
        update_bind_mounts(self._container, self._config, env_home_path())

        self.update_locale()

        username = os.environ['USER']
        uid = str(os.getuid())
        self.run_in_container("userdel -r ubuntu")
        self.run_in_container("useradd -u {} -U -p {} -G sudo,audio,video {}".format(
            uid, crypt.crypt(password or ''), username))
        self.run_in_container("mkdir -p /home/{}".format(username))
        self.run_in_container("chown {0}:{0} /home/{0}".format(username))

        self._create_libertine_user_data_dir()

        _setup_bind_mount_service(self._container, uid, username)
        _setup_etc_hosts(self._container)

        if multiarch and self.architecture == 'amd64':
            utils.get_logger().info("Adding i386 multiarch support to container '{}'".format(self.container_id))
            self.run_in_container("dpkg --add-architecture i386")

        self.update_packages()

        for package in self.default_packages:
            utils.get_logger().info("Installing package '%s' in container '%s'" % (package, self.container_id))
            if not self.install_package(package, no_dialog=True, update_cache=False):
                utils.get_logger().error("Failure installing '%s' during container creation" % package)
                self.destroy_libertine_container()
                return False

        super().create_libertine_container()

        lxd_stop(self._container)

        return True

    def install_package(self, package_name, no_dialog=False, update_cache=True):
        ret = super().install_package(package_name, no_dialog, update_cache)
        _add_local_files_for_ual(self._container)
        return ret

    def remove_package(self, package_name):
        ret = super().remove_package(package_name)
        _remove_local_files_for_ual(self._container)
        return ret

    def update_packages(self, update_locale=False):
        if not self._timezone_in_sync():
            utils.get_logger().info("Re-syncing timezones")
            self.run_in_container("bash -c 'echo \"%s\" > /etc/timezone'" % self._host_info.get_host_timezone())
            self.run_in_container("rm -f /etc/localtime")
            self.run_in_container("dpkg-reconfigure -f noninteractive tzdata")

        update_bind_mounts(self._container, self._config, env_home_path())
        _add_local_files_for_ual(self._container)
        _remove_local_files_for_ual(self._container)

        return super().update_packages(update_locale)

    def destroy_libertine_container(self, force):
        if not self._try_get_container():
            utils.get_logger().error("No such container '%s'" % self.container_id)
            return False

        if self._container.status == 'Running' and not force:
            utils.get_logger().error("Canceling destruction due to running container. Use --force to override.")
            return False

        lxd_start(self._container)
        dirs = ' '.join(['{}/*'.format(d) for d in _CONTAINER_DATA_DIRS])
        self.run_in_container('bash -c "rm -rf {}"'.format(dirs))
        lxd_stop(self._container)

        self._container.delete()

        return self._delete_rootfs()

    def _timezone_in_sync(self):
        proc = subprocess.Popen(self._lxc_args('cat /etc/timezone'), stdout=subprocess.PIPE)
        out, err = proc.communicate()
        return out.decode('UTF-8').strip('\n') == self._host_info.get_host_timezone()

    def _lxc_args(self, command, environ={}):
        return _lxc_args(self.container_id, command, environ)

    def run_in_container(self, command):
        return subprocess.Popen(self._lxc_args(command, os.environ.copy())).wait()

    def start_container(self, home=env_home_path()):
        if not self._try_get_container():
            return False

        if not self._service.container_operation_start(self.container_id):
            return False

        if self._container.status == 'Running':
            return True

        requires_remount = self._container.status == 'Stopped'

        if requires_remount:
            update_libertine_profile(self._lxd_client)
            update_bind_mounts(self._container, self._config, home)

        self._config.update_container_install_status(self.container_id, "starting")
        if not lxd_start(self._container):
            self._service.container_stopped()
            self._config.update_container_install_status(self.container_id, self._container.status.lower())
            return False

        self._config.update_container_install_status(self.container_id, "running")

        if not _wait_for_network(self._container):
            utils.get_logger().warning("Network unavailable in container '{}'".format(self.container_id))

        if requires_remount:
            self.run_in_container("/usr/bin/libertine-lxd-mount-update")

        return True

    def stop_container(self, wait=False):
        if not self._try_get_container():
            return False

        stopped = False
        self._config.refresh_database()

        if self._service.container_operation_finished(self.container_id, self._app_name, self._pid):
            self._config.update_container_install_status(self.container_id, self._get_stop_type_string(self._freeze_on_stop))

            if lxd_stop(self._container, freeze_on_stop=self._freeze_on_stop):
                stopped = self._service.container_stopped(self.container_id)

            self._config.update_container_install_status(self.container_id, self._container.status.lower())

        return False

    def restart_container(self, wait=True):
        if not self._try_get_container():
            return False

        if self._container.status != 'Frozen':
            utils.get_logger().warning("Container {} is not frozen. Cannot restart.".format(self._container.name))
            return False

        if not (lxd_stop(self._container) and lxd_start(self._container)):
            return False

        return lxd_stop(self._container, freeze_on_stop=self._freeze_on_stop)

    def start_application(self, app_exec_line, environ):
        if not self._try_get_container():
            utils.get_logger().error("Could not get container '{}'".format(self.container_id))
            return None

        if utils.is_snap_environment():
            environ['HOME'] = '/home/{}'.format(environ['USER'])

        if not self.start_container(home=environ['HOME']):
            return False

        self._app_name = app_exec_line[0]

        args = self._lxc_args("sudo -E -u {} env PATH={}".format(environ['USER'], environ['PATH']), environ)

        args.extend(app_exec_line)

        proc = psutil.Popen(args)
        self._pid = proc.pid

        return proc

    def finish_application(self, app):
        app.wait()

        self.stop_container()

    def copy_file_to_container(self, source, dest):
        with open(source, 'rb') as f:
            return self._container.files.put(dest, f.read())

    def delete_file_in_container(self, path):
        return self.run_in_container('rm {}'.format(path))

    def _try_get_container(self):
        if self._container is None:
            self._container = lxd_container(self._lxd_client, self.container_id)

        return self._container is not None
