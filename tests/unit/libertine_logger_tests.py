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
import shutil

import libertine.utils

from testtools import TestCase
from testtools.matchers import Equals, NotEquals

class TestLogger(TestCase):
    def setUp(self):
        super(TestLogger, self).setUp()
        os.environ['LIBERTINE_DEBUG'] = '1'
        self.addCleanup(self.cleanup)

    def cleanup(self):
        if os.getenv('LIBERTINE_DEBUG', None) is not None:
            del os.environ['LIBERTINE_DEBUG']

    def test_logger_off_by_default(self):
        # Need to turn off for this test only!
        self.cleanup()
        os.unsetenv('LIBERTINE_DEBUG')
        l = libertine.utils.get_logger()
        self.assertTrue(l.disabled)

    def test_logger_on_with_env_var(self):
        l = libertine.utils.get_logger()
        self.assertFalse(l.disabled)

    def test_logger_only_inits_once(self):
        l1 = libertine.utils.get_logger()
        l2 = libertine.utils.get_logger()
        l3 = libertine.utils.get_logger()
        self.assertThat(len(l3.handlers), Equals(1))

