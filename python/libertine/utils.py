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

import json
import os
import psutil
import subprocess
import xdg.BaseDirectory as basedir

from gi import require_version
require_version('Libertine', '1')
from gi.repository import Libertine


def container_exists(container_id):
    container_config_file_path = get_libertine_database_file_path()
 
    if os.path.exists(container_config_file_path):
        with open(get_libertine_database_file_path()) as fd:
            container_list = json.load(fd)

        if container_list:
            for container in container_list['containerList']:
                if container['id'] == container_id:
                    return True

    return False


def get_libertine_container_rootfs_path(container_id):
    path = Libertine.container_path(container_id)

    if path is None:
        path = os.path.join(get_libertine_containers_dir_path(), container_id, 'rootfs')

    return path


def get_libertine_containers_dir_path():
    return basedir.save_cache_path('libertine-container')


def get_libertine_database_dir_path():
    return os.path.join(basedir.xdg_data_home, 'libertine')


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


def get_host_architecture():
    dpkg = subprocess.Popen(['dpkg', '--print-architecture'],
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
    if dpkg.wait() != 0:
        parser.error("Failed to determine the local architecture.")

    return dpkg.stdout.read().strip()


def create_libertine_user_data_dir(container_id):
    user_data = get_libertine_container_userdata_dir_path(container_id)

    if not os.path.exists(user_data):
        os.makedirs(user_data)


def get_libertine_lxc_socket():
    return '\0libertine_lxc_socket'


def get_libertine_lxc_pulse_socket_path():
    return os.path.join(get_libertine_runtime_dir(), 'pulse_socket')


def setup_window_manager(container_id):
    if os.path.exists(os.path.join(get_libertine_container_rootfs_path(container_id),
                                   'usr', 'bin', 'matchbox-window-manager')):
        return ['matchbox-window-manager', '-use_titlebar', 'no']
    else:
        return ['compiz']


def terminate_window_manager(window_manager):
    for child in window_manager.children():
        child.terminate()
