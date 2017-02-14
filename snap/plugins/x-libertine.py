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


import snapcraft.plugins.cmake
import utils # local

class LibertinePlugin(snapcraft.plugins.cmake.CMakePlugin):
    def __init__(self, name, options, project):
        super().__init__(name, options, project)

        deps = utils.BuildDependsParser()

        with open('debian/control') as control:
            for line in control.readlines():
                deps.parse(line)

        self.build_packages.extend(deps.deps)
        self.options.configflags.extend(['-DCMAKE_INSTALL_PREFIX=/usr'])

    @classmethod
    def schema(cls):
        return super().schema()

    def enable_cross_compilation(self):
        return super().enable_cross_compilation()

    def build(self):
        super().build()

        # Fix all shebangs to use the in-snap python.
        utils.fix_shebangs(self.installdir + '/usr/bin')
