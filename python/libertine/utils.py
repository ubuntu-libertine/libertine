#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (C) 2015 Canonical Ltd.
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
import shlex
import subprocess
import xdg.BaseDirectory as basedir

from gi import require_version
require_version('Libertine', '1')
from gi.repository import Libertine

def get_logger():
    logger = logging.getLogger('__libertine_logger__')

    # If someone else sets a handler before this, we wont run this!
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        logger.disabled = True

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(filename)s:'
                                      '%(lineno)d: '
                                      '%(levelname)s: '
                                      '%(funcName)s():\t'
                                      '%(message)s')

        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # Only enable the logger if we set this
    if os.getenv('LIBERTINE_DEBUG') is '1':
        logger.disabled = False

    return logger


def get_libertine_container_rootfs_path(container_id):
    path = Libertine.container_path(container_id)

    if path is None:
        path = os.path.join(get_libertine_containers_dir_path(), container_id, 'rootfs')

    return path


def get_libertine_containers_dir_path():
    xdg_cache_home = os.getenv('XDG_CACHE_HOME',
                                os.path.join(os.getenv('HOME'), '.cache'))

    return os.path.join(xdg_cache_home, 'libertine-container')


def get_libertine_database_dir_path():
    xdg_data_home = os.getenv('XDG_DATA_HOME',
                              os.path.join(os.getenv('HOME'), '.local', 'share'))

    libertine_database_dir = os.path.join(xdg_data_home, 'libertine')

    if not os.path.exists(libertine_database_dir):
        os.makedirs(libertine_database_dir)

    return libertine_database_dir


def get_libertine_database_file_path():
    return os.path.join(get_libertine_database_dir_path(), 'ContainersConfig.json')


def get_libertine_container_userdata_dir_path(container_id):
    path = Libertine.container_home_path(container_id)

    if path is None:
        path = os.path.join(basedir.xdg_data_home, 'libertine-container', 'user-data', container_id)

    return path


def get_user_runtime_dir():
    try:
        return basedir.get_runtime_dir()
    except KeyError:
        import tempfile
        return tempfile.mkdtemp()


def get_libertine_runtime_dir():
    return os.path.join(get_user_runtime_dir(), 'libertine')


def get_common_xdg_directories():
    return ['Documents', 'Music', 'Pictures', 'Videos', 'Downloads']


def create_libertine_user_data_dir(container_id):
    user_data = get_libertine_container_userdata_dir_path(container_id)

    if not os.path.exists(user_data):
        os.makedirs(user_data)

    config_path = os.path.join(user_data, ".config", "dconf")

    if not os.path.exists(config_path):
        os.makedirs(config_path)

    xdg_user_dirs = get_common_xdg_directories()

    for xdg_dir in xdg_user_dirs:
        xdg_path = os.path.join(user_data, xdg_dir)

        if not os.path.exists(xdg_path):
            os.makedirs(xdg_path)


def get_libertine_lxc_socket():
    return '\0libertine_lxc_socket'


def get_libertine_lxc_pulse_socket_path():
    return os.path.join(get_libertine_runtime_dir(), 'pulse_socket')


def setup_window_manager(container_id, enable_toolbars=False):
    if os.path.exists(os.path.join(get_libertine_container_rootfs_path(container_id),
                                   'usr', 'bin', 'matchbox-window-manager')):
        if enable_toolbars:
            return ['matchbox-window-manager']

        return ['matchbox-window-manager', '-use_titlebar', 'no']
    else:
        return ['compiz']


def terminate_window_manager(window_manager):
    for child in window_manager.children():
        child.terminate()
        child.wait()

    window_manager.terminate()
    window_manager.wait()


def refresh_libertine_scope():
    scopes_object_path = "/com/canonical/unity/scopes"
    invalidate_signal = "com.canonical.unity.scopes.InvalidateResults"
    libertine_scope_id = "libertine-scope.ubuntu_libertine-scope"

    gdbus_cmd = ("gdbus emit --session --object-path %s --signal %s %s" %
                 (scopes_object_path, invalidate_signal, libertine_scope_id))

    subprocess.Popen(shlex.split(gdbus_cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
