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


import fileinput
import os
import re
import shlex
import snapcraft.plugins.nil
import sys
import subprocess
import utils # local


def _arch():
    cmd = subprocess.Popen(shlex.split('dpkg-architecture -qDEB_HOST_ARCH_CPU'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = cmd.communicate()
    arch = str(out, 'utf-8').strip()
    if arch == 'amd64':
        return 'x86_64-linux-gnu'
    elif arch == 'armhf':
        return 'arm-linux-gnueabihf'
    elif arch == 'arm64':
        return 'aarch64-linux-gnu'

    return '{}-linux-gnu'.format(arch)


class LibertineDependenciesPlugin(snapcraft.plugins.nil.NilPlugin):
    def __init__(self, name, options, project):
        super().__init__(name, options, project)
        self._arch = _arch()

        deps_parser = utils.DependsParser()
        with open('debian/control') as control:
            for line in control.readlines():
                deps_parser.parse(line)
        self.stage_packages.extend(deps_parser.deps)

        self._ignore_duplicate_files()

    @classmethod
    def schema(cls):
        return super().schema()

    def enable_cross_compilation(self):
        return super().enable_cross_compilation()

    def env(self, root):
        return super().env(root) + ['ARCH={}'.format(self._arch)]

    # By design, snapcraft ignores all pre- and post-inst scripts which
    # result in a bunch of packages that just don't work.
    def _run_preinst_postinst(self):
        # We need to create the lxc-usernet
        if not os.path.exists(self.installdir + '/etc/lxc/lxc-usernet'):
            with open(self.installdir + '/etc/lxc/lxc-usernet', 'w') as f:
                f.write('# USERNAME TYPE BRIDGE COUNT')

        # We need to run update-alternatives to create /usr/bin/fakeroot
        admindir = self.installdir + '/var/lib/dpkg/alternatives'
        altdir = self.installdir + '/etc/alternatives'
        os.makedirs(admindir, exist_ok=True)
        os.makedirs(altdir, exist_ok=True)
        subprocess.Popen(shlex.split('\
                update-alternatives --admindir {0} --altdir {1} --install \
                    {2}/usr/bin/fakeroot fakeroot {2}/usr/bin/fakeroot-sysv 50 \
        		--slave {2}/usr/share/man/man1/fakeroot.1.gz \
        		fakeroot.1.gz {2}/usr/share/man/man1/fakeroot-sysv.1.gz \
        		--slave {2}/usr/share/man/man1/faked.1.gz \
        		faked.1.gz {2}/usr/share/man/man1/faked-sysv.1.gz \
        		--slave {2}/usr/share/man/es/man1/fakeroot.1.gz \
        		fakeroot.es.1.gz {2}/usr/share/man/es/man1/fakeroot-sysv.1.gz \
        		--slave {2}/usr/share/man/es/man1/faked.1.gz \
        		faked.es.1.gz {2}/usr/share/man/es/man1/faked-sysv.1.gz \
        		--slave {2}/usr/share/man/fr/man1/fakeroot.1.gz \
        		fakeroot.fr.1.gz {2}/usr/share/man/fr/man1/fakeroot-sysv.1.gz \
        		--slave {2}/usr/share/man/fr/man1/faked.1.gz \
        		faked.fr.1.gz {2}/usr/share/man/fr/man1/faked-sysv.1.gz \
        		--slave {2}/usr/share/man/sv/man1/fakeroot.1.gz \
        		fakeroot.sv.1.gz {2}/usr/share/man/sv/man1/fakeroot-sysv.1.gz \
        		--slave {2}/usr/share/man/sv/man1/faked.1.gz \
        		faked.sv.1.gz {2}/usr/share/man/sv/man1/faked-sysv.1.gz\
                '.format(admindir, altdir, self.installdir))).wait()
        subprocess.Popen(shlex.split('\
                update-alternatives --admindir {0} --altdir {1} --install \
                    {2}/usr/bin/fakeroot fakeroot {2}/usr/bin/fakeroot-tcp 30 \
        		--slave {2}/usr/share/man/man1/fakeroot.1.gz \
        		fakeroot.1.gz {2}/usr/share/man/man1/fakeroot-tcp.1.gz \
        		--slave {2}/usr/share/man/man1/faked.1.gz \
        		faked.1.gz {2}/usr/share/man/man1/faked-tcp.1.gz \
        		--slave {2}/usr/share/man/es/man1/fakeroot.1.gz \
        		fakeroot.es.1.gz {2}/usr/share/man/es/man1/fakeroot-tcp.1.gz \
        		--slave {2}/usr/share/man/es/man1/faked.1.gz \
        		faked.es.1.gz {2}/usr/share/man/es/man1/faked-tcp.1.gz \
        		--slave {2}/usr/share/man/fr/man1/fakeroot.1.gz \
        		fakeroot.fr.1.gz {2}/usr/share/man/fr/man1/fakeroot-tcp.1.gz \
        		--slave {2}/usr/share/man/fr/man1/faked.1.gz \
        		faked.fr.1.gz {2}/usr/share/man/fr/man1/faked-tcp.1.gz \
        		--slave {2}/usr/share/man/sv/man1/fakeroot.1.gz \
        		fakeroot.sv.1.gz {2}/usr/share/man/sv/man1/fakeroot-tcp.1.gz \
        		--slave {2}/usr/share/man/sv/man1/faked.1.gz \
        		faked.sv.1.gz {2}/usr/share/man/sv/man1/faked-tcp.1.gz\
                '.format(admindir, altdir, self.installdir))).wait()

    def _fix_symlinks(self):
        for root, dirs, files in os.walk(self.installdir):
            for f in files:
                path = '{}/{}'.format(root, f)
                if os.path.islink(path):
                    link = os.readlink(path)
                    if link.startswith('/'): # needs fixing
                        os.remove(path)
                        os.symlink(os.path.relpath(link, root), path)

    def _fix_fakeroot(self):
        for line in fileinput.FileInput('{}/usr/bin/fakeroot'.format(self.installdir), inplace=True):
            if line.startswith('FAKEROOT_PREFIX='):
                sys.stdout.write('FAKEROOT_PREFIX=${SNAP}/usr  # Updated by x-libertine.py\n')
            elif line.startswith('FAKEROOT_BINDIR='):
                sys.stdout.write('FAKEROOT_BINDIR=${SNAP}/usr/bin  # Updated by x-libertine.py\n')
            elif line.startswith('PATHS='):
                sys.stdout.write('PATHS=${FAKEROOT_PREFIX}/lib/%s/libfakeroot:' \
                                 '${FAKEROOT_PREFIX}/lib64/libfakeroot:' \
                                 '${FAKEROOT_PREFIX}/lib32/libfakeroot' \
                                 '  # Updated by x-libertine.py\n' % self._arch)
            else:
                sys.stdout.write(line)

    def _ignore_duplicate_files(self):
        self.options.stage.extend([
            '-usr/lib/{}/liblibertine.so*'.format(self._arch),
            '-usr/bin/libertine*',
            '-etc/sudoers.d/libertine*',
            '-usr/lib/python3/dist-packages/libertine',
            '-usr/share/bash-completion/completions/*'
        ])

    def build(self):
        super().build()

        utils.fix_shebangs(self.installdir + '/usr/bin')

        self._run_preinst_postinst()
        self._fix_symlinks()
        self._fix_fakeroot()
