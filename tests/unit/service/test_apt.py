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

import os
import unittest.mock
from unittest import TestCase
from libertine.service import apt


def build_mock_app(name, summary, website, description):
    app = unittest.mock.Mock()
    app.name = name
    version = unittest.mock.Mock()
    version.summary = summary
    version.homepage = website
    version.description = description
    app.versions = [version]
    return app


class TestAptCache(TestCase):
    def test_search_returns_empty_when_no_matching_results(self):
        with unittest.mock.patch('libertine.service.apt.apt.Cache') as MockCache:
            MockCache.return_value.keys.return_value = []

            with unittest.mock.patch('libertine.service.apt.Libertine') as MockLibertine:
                MockLibertine.container_path.return_value = '/some/junk'
                self.assertEqual(apt.AptCache('palpatine').search('vim'), [])

    def test_search_returns_matching_results(self):
        with unittest.mock.patch('libertine.service.apt.apt.Cache') as MockCache:
            MockCache.return_value = {
                "vim": build_mock_app("vim", "vi improved", "vim.com", "who even uses raw vi"),
                "gedit": build_mock_app("gedit", "text editor", "gedit.com", "visual text editor"),
                "gimp": build_mock_app("gimp", "foss photoshop", "gimp.com", "edit bitmap images"),
                "vim-common": build_mock_app("vim-common", "common vim stuff", "vim.common", "dependencies")
            }

            with unittest.mock.patch('libertine.service.apt.Libertine') as MockLibertine:
                MockLibertine.container_path.return_value = '/some/junk'
                results = apt.AptCache('palpatine').search('vim')

            self.assertEqual(len(results), 2)
            results = sorted(results, key=lambda xx: xx['id'])
            self.assertEqual(results[0]['description'], 'who even uses raw vi')
            self.assertEqual(results[0]['name'], 'vim')
            self.assertEqual(results[0]['id'], 'vim')
            self.assertEqual(results[0]['summary'], 'vi improved')
            self.assertEqual(results[0]['website'], 'vim.com')
            self.assertEqual(results[0]['package'], 'vim')

            self.assertEqual(results[1]['description'], 'dependencies')
            self.assertEqual(results[1]['name'], 'vim-common')
            self.assertEqual(results[1]['id'], 'vim-common')
            self.assertEqual(results[1]['summary'], 'common vim stuff')
            self.assertEqual(results[1]['website'], 'vim.common')
            self.assertEqual(results[1]['package'], 'vim-common')

            MockCache.assert_called_once_with()

    def test_app_info_returns_empty_dict_when_no_such_app_exists(self):
        with unittest.mock.patch('libertine.service.apt.apt.Cache') as MockCache:
            MockCache.return_value = {}
            with unittest.mock.patch('libertine.service.apt.Libertine') as MockLibertine:
                MockLibertine.container_path.return_value = '/some/junk'
                self.assertEqual(apt.AptCache('palpatine').app_info("vim"), {})
            MockCache.assert_called_once_with()

    def test_app_info_returns_values_for_app(self):
        with unittest.mock.patch('libertine.service.apt.apt.Cache') as MockCache:
            MockCache.return_value = {
                "vim": build_mock_app("vim", "vi improved", "vim.com", "who even uses raw vi"),
                "gimp": build_mock_app("gimp", "foss photoshop", "gimp.com", "visual text editor"),
            }
            with unittest.mock.patch('libertine.service.apt.Libertine') as MockLibertine:
                MockLibertine.container_path.return_value = '/some/junk'
                self.assertEqual(apt.AptCache('palpatine').app_info("vim"), {
                    'name': 'vim',
                    'id': 'vim',
                    'package': 'vim',
                    'summary': 'vi improved',
                    'description': 'who even uses raw vi',
                    'website': 'vim.com'
                })
            MockCache.assert_called_once_with()

    def test_loads_cache_from_container_directory(self):
        with unittest.mock.patch('libertine.service.apt.apt.Cache') as MockCache:
            MockCache.return_value = {
                "vim": build_mock_app("vim", "vi improved", "vim.com", "who even uses raw vi"),
                "gimp": build_mock_app("gimp", "foss photoshop", "gimp.com", "visual text editor"),
            }
            with unittest.mock.patch('libertine.service.apt.Libertine') as MockLibertine:
                containerpath = "%s/containerroot" % os.path.dirname(os.path.realpath(__file__))
                MockLibertine.container_path.return_value = containerpath
                self.assertEqual(apt.AptCache('palpatine').app_info("vim"), {
                    'name': 'vim',
                    'id': 'vim',
                    'package': 'vim',
                    'summary': 'vi improved',
                    'description': 'who even uses raw vi',
                    'website': 'vim.com'
                })

            MockCache.assert_called_once_with(rootdir=containerpath)

    def test_loads_cache_only_once(self):
        with unittest.mock.patch('libertine.service.apt.apt.Cache') as MockCache:
            MockCache.return_value = {
                "vim": build_mock_app("vim", "vi improved", "vim.com", "who even uses raw vi"),
                "gimp": build_mock_app("gimp", "foss photoshop", "gimp.com", "visual text editor"),
            }
            with unittest.mock.patch('libertine.service.apt.Libertine') as MockLibertine:
                MockLibertine.container_path.return_value = '/some/junk'
                cache = apt.AptCache('palpatine')
                cache.app_info("vim")
                cache.app_info("vim")

            MockCache.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
