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

import os
from testtools import TestCase
from testtools.matchers import Equals
from gi.repository import Libertine
from unittest import skip
from unittest.mock import patch


class TestLibertineGir(TestCase):

    def setUp(self):
        super(TestLibertineGir, self).setUp()
        self.cmake_source_dir = os.environ['LIBERTINE_DATA_DIR']

    def test_list_containers(self):
        with patch.dict('os.environ', {'XDG_DATA_HOME': self.cmake_source_dir + '/libertine-config', 'IGNORE_SNAP': '1'}):
            containers = Libertine.list_containers()

            self.assertThat(containers[0], Equals('wily'))
            self.assertThat(containers[1], Equals('wily-2'))

    @skip("need to work around cached globals in glib")
    def test_container_path(self):
        container_id = 'wily'
        with patch.dict('os.environ', {'XDG_CACHE_HOME': self.cmake_source_dir + '/libertine-data', 'IGNORE_SNAP': '1'}):
            container_path = Libertine.container_path(container_id)

            self.assertThat(container_path, Equals(self.cmake_source_dir + '/libertine-data/libertine-container/wily/rootfs'))

    def test_container_home_path(self):
        container_id = 'wily'
        with patch.dict('os.environ', {'XDG_DATA_HOME': self.cmake_source_dir + '/libertine-home', 'IGNORE_SNAP': '1'}):
            container_home_path = Libertine.container_home_path(container_id)

            self.assertThat(container_home_path, Equals(self.cmake_source_dir + '/libertine-home/libertine-container/user-data/wily'))

    def test_container_name(self):
        with patch.dict('os.environ', {'XDG_DATA_HOME': self.cmake_source_dir + '/libertine-config', 'IGNORE_SNAP': '1'}):
            container_name = Libertine.container_name('wily')

            self.assertThat(container_name, Equals("Ubuntu 'Wily Werewolf'"))

            container_name = Libertine.container_name('wily-2')

            self.assertThat(container_name, Equals("Ubuntu 'Wily Werewolf' (2)"))

    def test_list_apps_for_container(self):
        with patch.dict('os.environ', {'XDG_DATA_HOME': self.cmake_source_dir + '/libertine-config', 'IGNORE_SNAP': '1'}):
            apps = Libertine.list_apps_for_container('wily')

            self.assertThat(len(apps), Equals(0))
