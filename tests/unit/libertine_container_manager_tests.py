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

import json
import os
import shlex
import shutil
import subprocess

from testtools import TestCase
from testtools.matchers import Equals, NotEquals

class TestLibertineCLI(TestCase):

    def setUp(self):
        super(TestLibertineCLI, self).setUp()
        self.cmake_source_dir = os.environ['CMAKE_SOURCE_DIR']
        self.cmake_binary_dir = os.environ['CMAKE_BINARY_DIR']

    def get_container_config_path(self):
        return os.path.join(self.cmake_binary_dir, 'tests', 'unit', 'libertine-config')

    def get_container_config_file(self):
        return os.path.join(self.get_container_config_path(), 'libertine', 'ContainersConfig.json')

    def get_container_json_object(self):
        container_list = {}
        container_config_file = self.get_container_config_file()

        if os.path.exists(container_config_file):
            with open(container_config_file, 'r') as fd:
                container_list = json.load(fd)

            fd.close()

        return container_list
        
    def test_01_create_initial_container(self):
        os.environ['XDG_DATA_HOME'] = self.get_container_config_path()

        if os.path.exists(self.get_container_config_file()):
            shutil.rmtree(self.get_container_config_path())

        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager create -i test -n Test -t mock'
        args = shlex.split(cli_cmd)

        subprocess.Popen(args).wait()

        container_list = self.get_container_json_object()

        self.assertThat(len(container_list), NotEquals(0))
        self.assertThat(len(container_list['containerList']), Equals(1))
        self.assertThat(container_list['containerList'][0]['id'], Equals('test'))
        self.assertThat(container_list['containerList'][0]['name'], Equals('Test'))
        self.assertThat(container_list['defaultContainer'], Equals('test'))

    def test_02_create_second_container(self):
        os.environ['XDG_DATA_HOME'] = self.get_container_config_path()
        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager create -i test2 -n Test2 -t mock'
        args = shlex.split(cli_cmd)

        subprocess.Popen(args).wait()

        container_list = self.get_container_json_object()

        self.assertThat(len(container_list), NotEquals(0))
        self.assertThat(len(container_list['containerList']), Equals(2))
        self.assertThat(container_list['containerList'][1]['id'], Equals('test2'))
        self.assertThat(container_list['containerList'][1]['name'], Equals('Test2'))
        self.assertThat(container_list['defaultContainer'], Equals('test'))

    def test_03_create_existing_container(self):
        os.environ['XDG_DATA_HOME'] = self.get_container_config_path()
        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager create -i test -n Test -t mock'
        args = shlex.split(cli_cmd)

        p = subprocess.Popen(args)
        p.wait()

        # Return code of 1 indicates the cli found the container already exists.
        self.assertThat(p.returncode, Equals(1))

    def test_04_add_package_to_initial_container(self):
        os.environ['XDG_DATA_HOME'] = self.get_container_config_path()

        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager install-package -i test -p firefox'
        args = shlex.split(cli_cmd)

        subprocess.Popen(args).wait()

        container_list = self.get_container_json_object()

        self.assertThat(len(container_list), NotEquals(0))
        self.assertThat(len(container_list['containerList'][0]['installedApps']), NotEquals(0))
        self.assertThat(container_list['containerList'][0]['installedApps'][0]['packageName'], Equals('firefox'))

    def test_05_add_second_package_to_initial_container(self):
        os.environ['XDG_DATA_HOME'] = self.get_container_config_path()

        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager install-package -i test -p libreoffice'
        args = shlex.split(cli_cmd)

        subprocess.Popen(args).wait()

        container_list = self.get_container_json_object()

        self.assertThat(len(container_list), NotEquals(0))
        self.assertThat(len(container_list['containerList'][0]['installedApps']), NotEquals(0))
        self.assertThat(container_list['containerList'][0]['installedApps'][1]['packageName'], Equals('libreoffice'))

    def test_06_add_package_to_second_container(self):
        os.environ['XDG_DATA_HOME'] = self.get_container_config_path()

        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager install-package -i test2 -p gedit'
        args = shlex.split(cli_cmd)

        subprocess.Popen(args).wait()

        container_list = self.get_container_json_object()

        self.assertThat(len(container_list), NotEquals(0))
        self.assertThat(len(container_list['containerList'][1]['installedApps']), NotEquals(0))
        self.assertThat(container_list['containerList'][1]['installedApps'][0]['packageName'], Equals('gedit'))

    def test_07_add_existing_package_to_initial_container(self):
        os.environ['XDG_DATA_HOME'] = self.get_container_config_path()

        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager install-package -i test -p firefox'
        args = shlex.split(cli_cmd)

        p = subprocess.Popen(args)
        p.wait()

        # Return code of 1 indicates the cli found the package already exists.
        self.assertThat(p.returncode, Equals(1))

    def test_08_remove_package_from_second_container(self):
        os.environ['XDG_DATA_HOME'] = self.get_container_config_path()

        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager remove-package -i test2 -p gedit'
        args = shlex.split(cli_cmd)

        subprocess.Popen(args).wait()

        container_list = self.get_container_json_object()

        self.assertThat(len(container_list), NotEquals(0))
        self.assertThat(len(container_list['containerList'][1]['installedApps']), Equals(0))

    def test_09_remove_package_from_initial_container(self):
        os.environ['XDG_DATA_HOME'] = self.get_container_config_path()

        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager remove-package -i test -p firefox'
        args = shlex.split(cli_cmd)

        subprocess.Popen(args).wait()

        container_list = self.get_container_json_object()

        self.assertThat(len(container_list), NotEquals(0))
        self.assertThat(len(container_list['containerList'][0]['installedApps']), Equals(1))
        self.assertThat(container_list['containerList'][0]['installedApps'][0]['packageName'], Equals('libreoffice'))

    def test_10_remove_initial_container(self):
        os.environ['XDG_DATA_HOME'] = self.get_container_config_path()

        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager destroy -i test'
        args = shlex.split(cli_cmd)

        subprocess.Popen(args).wait()

        container_list = self.get_container_json_object()

        self.assertThat(len(container_list), NotEquals(0))
        self.assertThat(container_list['containerList'][0]['id'], Equals('test2'))
        self.assertThat(container_list['containerList'][0]['name'], Equals('Test2'))
        self.assertThat(container_list['defaultContainer'], Equals('test2'))

    def test_11_remove_last_container(self):
        os.environ['XDG_DATA_HOME'] = self.get_container_config_path()

        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager destroy -i test2'
        args = shlex.split(cli_cmd)

        subprocess.Popen(args).wait()

        container_list = self.get_container_json_object()

        self.assertThat(len(container_list), NotEquals(0))
        self.assertThat(len(container_list['containerList']), Equals(0))
        self.assertThat('defaultContainer' not in container_list, Equals(True))
