# -*- coding: utf-8 -*-

# Copyright (C) 2015-2017 Canonical Ltd.
# Author: Christopher Townsend <christopher.townsend@canonical.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
import psutil
import shlex
import subprocess
import xdg.BaseDirectory as basedir

import gettext
gettext.textdomain('libertine')
_ = gettext.gettext


def get_logger():
    logger = logging.getLogger('__libertine_logger__')

    # If someone else sets a handler before this, we wont run this!
    if not logger.hasHandlers():
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(filename)s:'
                                      '%(lineno)d: '
                                      '%(levelname)s: '
                                      '%(funcName)s():\t'
                                      '%(message)s')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if 'LIBERTINE_DEBUG' in os.environ:
        if os.environ['LIBERTINE_DEBUG'] == '0':
            logger.setLevel(logging.WARNING)
        elif os.environ['LIBERTINE_DEBUG'] == '1':
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    return logger


def set_environmental_verbosity(verbosity):
    # Set debug levels if not overridden in environment
    if 'LIBERTINE_DEBUG' not in os.environ:
        if verbosity is None:
            os.environ['LIBERTINE_DEBUG'] = '1'
        else:
            os.environ['LIBERTINE_DEBUG'] = str(verbosity)


def get_libertine_container_rootfs_path(container_id):
    return os.path.join(get_libertine_containers_dir_path(), container_id, 'rootfs')


def get_libertine_containers_dir_path():
    if is_snap_environment():
        libertine_cache_home = os.path.join(os.getenv('SNAP_USER_COMMON'), '.cache')
    else:
        libertine_cache_home = os.getenv('XDG_CACHE_HOME',
                                    os.path.join(os.getenv('HOME'), '.cache'))

    return os.path.join(libertine_cache_home, 'libertine-container')


def get_libertine_database_dir_path():
    if is_snap_environment():
        xdg_data_home = os.path.join(os.getenv('SNAP_USER_COMMON'), '.local', 'share')
    else:
        xdg_data_home = os.getenv('XDG_DATA_HOME',
                            os.path.join(os.getenv('HOME'), '.local', 'share'))

    libertine_database_dir = os.path.join(xdg_data_home, 'libertine')

    os.makedirs(libertine_database_dir, exist_ok=True)

    return libertine_database_dir


def get_libertine_database_file_path():
    return os.path.join(get_libertine_database_dir_path(), 'ContainersConfig.json')


def get_libertine_container_home_dir(container_id):
    path = os.path.join(basedir.xdg_data_home, 'libertine-container', 'user-data', container_id)

    if is_snap_environment():
        path = path.replace(os.environ['HOME'], os.getenv('SNAP_USER_COMMON'))

    return path


def get_user_runtime_dir():
    try:
        return basedir.get_runtime_dir()
    except KeyError:
        import tempfile
        return tempfile.mkdtemp()


def get_libertine_runtime_dir():
    return os.path.join(get_user_runtime_dir(), 'libertine')


def generate_binding_directories(dirs, prefix):
    names = []
    binding_dirs = []
    for dir in set(dirs): # iterate over unique items
        if len([d for d in dirs if dir.startswith(d)]) > 1: # exclude if subset of other dir
            continue

        name = dir
        if name.startswith(prefix):
            name = name.replace(prefix, '', 1).lstrip('/')

        if name in names:
            binding_dirs.append((dir, "%s (%i)" % (name, names.count(name))))
        else:
            binding_dirs.append((dir, name))
        names.append(name)

    return binding_dirs


def get_common_xdg_user_directories():
    dirs = []
    for dir in ['DOCUMENTS', 'MUSIC', 'PICTURES', 'VIDEOS', 'DOWNLOAD']:
        xdg = subprocess.Popen(["xdg-user-dir", dir], stdout=subprocess.PIPE)
        stdout, stderr = xdg.communicate()
        dirs.append(stdout.decode('utf-8').strip())
    return dirs


def get_libertine_lxc_pulse_socket_path():
    return os.path.join(get_libertine_runtime_dir(), 'pulse_socket')


def refresh_libertine_scope():
    scopes_object_path = "/com/canonical/unity/scopes"
    invalidate_signal = "com.canonical.unity.scopes.InvalidateResults"
    libertine_scope_id = "libertine-scope.ubuntu_libertine-scope"

    gdbus_cmd = ("gdbus emit --session --object-path %s --signal %s %s" %
                 (scopes_object_path, invalidate_signal, libertine_scope_id))

    subprocess.Popen(shlex.split(gdbus_cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def set_session_dbus_env_var():
    dbus_session_set = 'SESSION' in os.environ

    try:
        if not dbus_session_set:
            for p in psutil.process_iter():
                try:
                    if p.name() == 'unity8' or p.name() == 'compiz':
                        p_environ = subprocess.check_output(["cat", "/proc/{}/environ".format(p.pid)])
                        for line in p_environ.decode().split('\0'):
                            if line.startswith('DBUS_SESSION_BUS_ADDRESS'):
                                os.environ['DBUS_SESSION_BUS_ADDRESS'] = line.partition('DBUS_SESSION_BUS_ADDRESS=')[2].rstrip('\n')
                                dbus_session_set = True
                                break
                        break
                except psutil.NoSuchProcess as e:
                    get_logger().warning(str(e))
    except subprocess.CalledProcessError as e:
        get_logger().warning(utils._("Exception caught while setting session dbus address: {error}").format(error=str(e)))
        dbus_session_set = 'DBUS_SESSION_BUS_ADDRESS' in os.environ

    return dbus_session_set


def is_snap_environment():
    return 'SNAP' in os.environ


def get_deb_package_name(package):
    pkg_name_proc = subprocess.Popen(shlex.split('dpkg --field {} Package'.format(package)), stdout=subprocess.PIPE)
    out, err = pkg_name_proc.communicate()
    return out.decode('utf-8').strip()
