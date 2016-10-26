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

import logging
import os

import libertine.utils

from testtools import TestCase
from testtools.matchers import Equals, NotEquals
from unittest.mock import patch


class TestLogger(TestCase):

    def test_logger_off_by_default(self):
        with patch.dict('os.environ'):
            if 'LIBERTINE_DEBUG' in os.environ:
                del os.environ['LIBERTINE_DEBUG']
            l = libertine.utils.get_logger()
            self.assertThat(l.getEffectiveLevel(), Equals(logging.WARNING))

    def test_logger_on_with_env_var(self):
        with patch.dict('os.environ', {'LIBERTINE_DEBUG': '1'}):
            l = libertine.utils.get_logger()
            self.assertThat(l.getEffectiveLevel(), Equals(logging.DEBUG))

    def test_logger_only_inits_once(self):
        with patch.dict('os.environ', {'LIBERTINE_DEBUG': '1'}):
            l1 = libertine.utils.get_logger()
            l2 = libertine.utils.get_logger()
            l3 = libertine.utils.get_logger()
            self.assertThat(len(l3.handlers), Equals(1))

