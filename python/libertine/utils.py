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

import os
import xdg.BaseDirectory as basedir

from gi import require_version
require_version('Libertine', '1')
from gi.repository import Libertine


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
    return basedir.get_runtime_dir()
