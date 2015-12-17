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
import shlex
import subprocess

from testtools import TestCase
from testtools.matchers import Equals, NotEquals

class TestLibertineLaunch(TestCase):

    def setUp(self):
        super(TestLibertineLaunch, self).setUp()
        self.cmake_source_dir = os.environ['CMAKE_SOURCE_DIR']
        self.cmake_binary_dir = os.environ['CMAKE_BINARY_DIR']

        # Set the paths to the config file
        container_config_path = os.path.join(self.cmake_binary_dir, 'tests', 'unit', 'libertine-config')
        container_config_file = os.path.join(container_config_path, 'libertine', 'ContainersConfig.json')

        # Set necessary enviroment variables
        os.environ['XDG_DATA_HOME'] = container_config_path
        os.environ['DISPLAY'] = ':0'
        os.environ['PATH'] = (self.cmake_source_dir + '/tests/mocks:' +
                              self.cmake_source_dir + '/tools:' + os.environ['PATH'])

        # Make a mock container
        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager create -i test -n Test -t mock'
        args = shlex.split(cli_cmd)
        subprocess.Popen(args).wait()
    
    def test_launch_app_existing_container(self):
        '''
        Base line test to ensure launching an app in an existing container works.
        '''
        cli_cmd = self.cmake_source_dir + '/tools/libertine-launch test true'
        args = shlex.split(cli_cmd)
        p = subprocess.Popen(args)
        p.wait()

        self.assertThat(p.returncode, Equals(0))

    def test_launch_app_nonexistent_container(self):
        '''
        Test to make sure that things gracefully handle a non-existing container.
        '''
        cli_cmd = self.cmake_source_dir + '/tools/libertine-launch test1 true'
        args = shlex.split(cli_cmd)
        p = subprocess.Popen(args)
        p.wait()

        # Should fail due to nonexistent container
        self.assertThat(p.returncode, Equals(1))

    def test_launch_good_app(self):
        '''
        Test to make sure that launching an app actually works.
        '''
        cli_cmd = self.cmake_source_dir + '/tools/libertine-launch test mock_app'
        args = shlex.split(cli_cmd)
        p = subprocess.Popen(args)
        p.wait()

        self.assertThat(p.returncode, Equals(0))
        self.assertThat(os.path.exists(os.path.join(self.cmake_binary_dir, 'mock')), Equals(True))

        os.remove(os.path.join(self.cmake_binary_dir, 'mock'))

    def test_launch_bad_app(self):
        '''
        Test to make sure launching an app that doesn't exist doesn't break things
        '''
        cli_cmd = self.cmake_source_dir + '/tools/libertine-launch test foo'
        args = shlex.split(cli_cmd)
        p = subprocess.Popen(args)
        p.wait()

        self.assertThat(p.returncode, Equals(1))
