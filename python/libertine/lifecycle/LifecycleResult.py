#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (C) 2016 Canonical Ltd.

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

class LifecycleResult(object):
    def __init__(self, error=''):
        self._error = error

    @property
    def error(self):
        return self._error or ''

    @property
    def success(self):
        return self.error == ''

    @classmethod
    def from_dict(kls, d):
        return LifecycleResult(d.get('error', None))

    def to_dict(self):
        return {
            'error': self.error
        }
