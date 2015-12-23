"""Unit tests for the LibertineContainer interface."""
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

from libertine import Libertine
from testtools import TestCase
from testtools.matchers import Equals
import os
import shutil
import tempfile


class TestLibertineContainer(TestCase):

    def setUp(self):
        super().setUp()
        self._working_dir = tempfile.mkdtemp()
        os.environ['XDG_CACHE_HOME'] = self._working_dir
        os.environ['XDG_DATA_HOME'] = self._working_dir

    def tearDown(self):
        shutil.rmtree(self._working_dir)
        super().tearDown()

    def test_container_id(self):
        container_id = "test-id-1"
        container = Libertine.LibertineContainer(container_id)

        self.assertThat(container.container_id, Equals(container_id))

    def test_container_type_default(self):
        container_id = "test-id-2"
        container = Libertine.LibertineContainer(container_id)

        self.assertThat(container.container_type, Equals("lxc"))

    def test_container_name_default(self):
        container_id = "test-id-3"
        container = Libertine.LibertineContainer(container_id)

        self.assertThat(container.name, Equals("Unknown"))

    def test_container_root_path(self):
        container_id = "test-id-4"
        container = Libertine.LibertineContainer(container_id)

        expected_root_path = os.path.join(self._working_dir,
                                          "libertine-container",
                                          container_id,
                                          "rootfs")
        self.assertThat(container.root_path, Equals(expected_root_path))
