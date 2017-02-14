# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2016 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from snapcraft import file_utils


def fix_shebangs(path):
    file_utils.replace_in_file(path, re.compile(r''),
                               re.compile(r'^#!.*python'),
                               r'#!/usr/bin/env python')


def _sanitize(dep):
    return re.sub(r"\(.*\)", "", re.sub(r"\[.*\]", "", dep)).replace(',', '').strip()


class DependsParser(object):
    def __init__(self):
        self.keyword = 'Depends:'
        self._parsing = False
        self._deps = []
        self._packages = []

    @property
    def deps(self):
        return [dep for dep in self._deps if dep not in self._packages]

    def parse(self, line):
        if self._parsing:
            if ':' in line:
                if not line.strip().startswith('${'):
                    self._parsing = False
            else:
                self._deps.append(_sanitize(line))

        if line.startswith(self.keyword):
            self._parsing = True
            possible_dep = line.lstrip(self.keyword)
            if not possible_dep.isspace() and not possible_dep.strip().startswith('${'):
                self._deps.append(_sanitize(possible_dep))

        if line.startswith('Package:'):
            self._packages.append(line.lstrip('Package:').strip())


class BuildDependsParser(DependsParser):
    def __init__(self):
        super().__init__()
        self.keyword = 'Build-Depends:'
