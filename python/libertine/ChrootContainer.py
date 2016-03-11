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
import psutil
import shlex
import shutil
import subprocess
from .Libertine import BaseContainer
from . import utils


def chown_recursive_dirs(path):
    uid = None
    gid = None

    if 'SUDO_UID' in os.environ:
        uid = int(os.environ['SUDO_UID'])
    if 'SUDO_GID' in os.environ:
        gid = int(os.environ['SUDO_GID'])

    if uid is not None and gid is not None:
        for root, dirs, files in os.walk(path):
            for d in dirs:
                os.chown(os.path.join(root, d), uid, gid)
            for f in files:
                os.chown(os.path.join(root, f), uid, gid)

        os.chown(path, uid, gid)


class LibertineChroot(BaseContainer):
    """
    A concrete container type implemented using a plain old chroot.
    """

    def __init__(self, container_id):
        super().__init__(container_id)
        self.container_type = "chroot"
        os.environ['FAKECHROOT_CMD_SUBST'] = '$FAKECHROOT_CMD_SUBST:/usr/bin/chfn=/bin/true'
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'

    def run_in_container(self, command_string):
        cmd_args = shlex.split(command_string)
        if self.get_container_distro(self.container_id) == "trusty":
            proot_cmd = '/usr/bin/proot'
            if not os.path.isfile(proot_cmd) or not os.access(proot_cmd, os.X_OK):
                raise RuntimeError('executable proot not found')
            command_prefix = proot_cmd + " -b /usr/lib/locale -S " + self.root_path
        else:
            command_prefix = "fakechroot fakeroot chroot " + self.root_path
        args = shlex.split(command_prefix + ' ' + command_string)
        cmd = subprocess.Popen(args)
        return cmd.wait()

    def destroy_libertine_container(self):
        shutil.rmtree(self.root_path)

    def create_libertine_container(self, password=None, verbosity=1):
        installed_release = self.get_container_distro(self.container_id)

        # Create the actual chroot
        if installed_release == "trusty":
            command_line = "debootstrap --verbose " + installed_release + " " + self.root_path
        else:
            command_line = "fakechroot fakeroot debootstrap --verbose --variant=fakechroot {} {}".format(
                    installed_release, self.root_path)
        args = shlex.split(command_line)
        subprocess.Popen(args).wait()

        # Remove symlinks as they can ill-behaved recursive behavior in the chroot
        if installed_release != "trusty":
            print("Fixing chroot symlinks...")
            os.remove(os.path.join(self.root_path, 'dev'))
            os.remove(os.path.join(self.root_path, 'proc'))

            with open(os.path.join(self.root_path, 'usr', 'sbin', 'policy-rc.d'), 'w+') as fd:
                fd.write("#!/bin/sh\n\n")
                fd.write("while true; do\n")
                fd.write("case \"$1\" in\n")
                fd.write("  -*) shift ;;\n")
                fd.write("  makedev) exit 0;;\n")
                fd.write("  *)  exit 101;;\n")
                fd.write("esac\n")
                fd.write("done\n")
                os.fchmod(fd.fileno(), 0o755)

        # Add universe, multiverse, and -updates to the chroot's sources.list
        if (utils.get_host_architecture() == 'armhf'):
            archive = "deb http://ports.ubuntu.com/ubuntu-ports "
        else:
            archive = "deb http://archive.ubuntu.com/ubuntu "

        if verbosity == 1:
            print("Updating chroot's sources.list entries...")
        with open(os.path.join(self.root_path, 'etc', 'apt', 'sources.list'), 'a') as fd:
            fd.write(archive + installed_release + "-updates main\n")
            fd.write(archive + installed_release + " universe\n")
            fd.write(archive + installed_release + "-updates universe\n")
            fd.write(archive + installed_release + " multiverse\n")
            fd.write(archive + installed_release + "-updates multiverse\n")

        utils.create_libertine_user_data_dir(self.container_id)

        if installed_release == "trusty":
            print("Additional configuration for Trusty chroot...")

            proot_cmd = '/usr/bin/proot'
            if not os.path.isfile(proot_cmd) or not os.access(proot_cmd, os.X_OK):
                raise RuntimeError('executable proot not found')
            cmd_line_prefix = proot_cmd + " -b /usr/lib/locale -S " + self.root_path

            command_line = cmd_line_prefix + " dpkg-divert --local --rename --add /etc/init.d/systemd-logind"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " dpkg-divert --local --rename --add /sbin/initctl"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " dpkg-divert --local --rename --add /sbin/udevd"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " dpkg-divert --local --rename --add /usr/sbin/rsyslogd"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " ln -s /bin/true /etc/init.d/systemd-logind"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " ln -s /bin/true /sbin/initctl"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " ln -s /bin/true /sbin/udevd"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

            command_line = cmd_line_prefix + " ln -s /bin/true /usr/sbin/rsyslogd"
            args = shlex.split(command_line)
            cmd = subprocess.Popen(args).wait()

        if verbosity == 1:
            print("Updating the contents of the container after creation...")
        self.update_packages(verbosity)
        self.install_package("libnss-extrausers", verbosity)
        self.install_package("software-properties-common", verbosity)

        if verbosity == 1:
            print("Installing Matchbox as the Xmir window manager...")
        self.install_package('matchbox', verbosity)

        # Check if the container was created as root and chown the user directories as necessary
        chown_recursive_dirs(utils.get_libertine_container_userdata_dir_path(self.container_id))

    def _build_proot_command(self):
        proot_cmd = '/usr/bin/proot'
        if not os.path.isfile(proot_cmd) or not os.access(proot_cmd, os.X_OK):
            raise RuntimeError('executable proot not found')

        proot_cmd += " -R " + self.root_path

        # Bind-mount the host's locale(s)
        proot_cmd += " -b /usr/lib/locale"

        # Bind-mount extrausers on the phone
        if os.path.exists("/var/lib/extrausers"):
            proot_cmd += " -b /var/lib/extrausers"

        home_path = os.environ['HOME']

        # Bind-mount common XDG direcotries
        bind_mounts = (
            " -b %s:%s"
            % (utils.get_libertine_container_userdata_dir_path(self.container_id), home_path)
        )

        xdg_user_dirs = ['Documents', 'Music', 'Pictures', 'Videos']
        for user_dir in xdg_user_dirs:
            user_dir_path = os.path.join(home_path, user_dir)
            bind_mounts += " -b %s:%s" % (user_dir_path, user_dir_path)

        proot_cmd += bind_mounts

        user_dconf_path = os.path.join(home_path, '.config', 'dconf')
        if os.path.exists(user_dconf_path):
            proot_cmd += " -b %s" % user_dconf_path

        return proot_cmd

    def launch_application(self, app_exec_line):
        # FIXME: Disabling seccomp is a temporary measure until we fully understand why we need
        #        it or figure out when we need it.
        os.environ['PROOT_NO_SECCOMP'] = '1'

        # Workaround issue where a custom dconf profile is on the machine
        if 'DCONF_PROFILE' in os.environ:
            del os.environ['DCONF_PROFILE']

        proot_cmd = self._build_proot_command()

        args = shlex.split(proot_cmd)
        args.extend(utils.setup_window_manager(self.container_id))
        window_manager = psutil.Popen(args)

        args = shlex.split(proot_cmd)
        args.extend(app_exec_line)
        psutil.Popen(args).wait()

        utils.terminate_window_manager(window_manager)
