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

import locale
import lsb_release
import os
import platform
import subprocess

from distro_info import UbuntuDistroInfo
from libertine import utils


class HostInfo(object):

    def select_container_type_by_kernel(self):
        if self.has_lxd_support():
            return "lxd"
        elif self.has_lxc_support():
            return "lxc"
        else:
            return "chroot"

    def has_lxc_support(self):
        kernel_release = platform.release().split('.')
        return int(kernel_release[0]) >= 4 or (int(kernel_release[0]) == 3 and int(kernel_release[1]) >= 13)

    def has_lxd_support(self):
        kernel_release = platform.release().split('.')
        return int(kernel_release[0]) >= 4 or (int(kernel_release[0]) == 4)

    def get_host_distro_release(self):
        distinfo = lsb_release.get_distro_information()

        return distinfo.get('CODENAME', 'n/a')

    def is_distro_valid(self, distro, force=False):
        if force:
            return UbuntuDistroInfo().valid(distro)

        if distro == self.get_host_distro_release():
            return True

        supported_distros = UbuntuDistroInfo().supported()

        try:
            supported_distros.index(distro)
        except ValueError:
            return False

        return True

    def get_distro_codename(self, distro):
        ubuntu_distro_info = UbuntuDistroInfo()

        for row in ubuntu_distro_info._rows:
            if row['series'] == distro:
                return row['codename']

        return None

    def get_host_architecture(self):
        if 'ARCH' in os.environ:
            return os.environ['ARCH']

        dpkg = subprocess.Popen(['dpkg', '--print-architecture'],
                                stdout=subprocess.PIPE,
                                universal_newlines=True)
        if dpkg.wait() != 0:
            parser.error(utils._("Failed to determine the local architecture."))

        return dpkg.stdout.read().strip()

    def get_host_timezone(self):
        with open(os.path.join('/', 'etc', 'timezone'), 'r') as fd:
            return fd.read().strip('\n')

    def get_host_locale(self):
        host_locale = locale.getlocale()
        full_locale = None

        if len(host_locale) == 2:
            full_locale = "{}.{}".format(host_locale[0], host_locale[1])
        elif len(host_locale) == 1:
            full_locale = "{}".format(host_locale[0])

        return full_locale
