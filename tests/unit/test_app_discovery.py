"""Unit tests for the AppLauncher module."""
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

from libertine.AppDiscovery import IconCache
from testtools import TestCase
from testtools.matchers import Equals


class TestIconSearching(TestCase):

    def mock_file_loader(self, root_path):
        return [
            "/some/path/128x128/icon.png",
            "/somepath/icon.png",
            "/somepath/testme.png"
            ];

    def test_full_path(self):
        some_root = "/some_root"
        icon_cache = IconCache(some_root, file_loader=self.mock_file_loader)

        some_full_path = "/this/is/a/full/path"
        self.assertThat(icon_cache.expand_icons(some_full_path)[0],
                        Equals(some_full_path))

    def test_icon_name(self):
        some_root = "/some_root"
        icon_cache = IconCache(some_root, file_loader=self.mock_file_loader)

        some_icon_list = "testme"
        self.assertThat(icon_cache.expand_icons(some_icon_list)[0],
                        Equals("/somepath/testme.png"))

    def test_edge_case_relative_file_name(self):
        some_root = "/some_root"
        icon_cache = IconCache(some_root, file_loader=self.mock_file_loader)

        some_icon_list = "testme.png"
        self.assertThat(icon_cache.expand_icons(some_icon_list)[0],
                        Equals("/somepath/testme.png"))
