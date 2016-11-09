# Copyright 2015-2016 Canonical Ltd.
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
from libertine.ContainersConfig import ContainersConfig


def chown_recursive_dirs(path):
    uid = 0
    gid = 0

    if 'SUDO_UID' in os.environ:
        uid = int(os.environ['SUDO_UID'])
    if 'SUDO_GID' in os.environ:
        gid = int(os.environ['SUDO_GID'])

    if uid != 0 and gid != 0:
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
        command_prefix = "fakechroot fakeroot chroot " + self.root_path
        args = shlex.split(command_prefix + ' ' + command_string)
        cmd = subprocess.Popen(args)
        return cmd.wait()

    def destroy_libertine_container(self):
        container_root = os.path.join(utils.get_libertine_containers_dir_path(), self.container_id)
        try:
            shutil.rmtree(container_root)
        except Exception as e:
            print("%s" % e)

    def create_libertine_container(self, password=None, multiarch=False, verbosity=1):
        # Create the actual chroot
        command_line = "fakechroot fakeroot debootstrap --verbose --variant=fakechroot {} {}".format(
                    self.installed_release, self.root_path)
        args = shlex.split(command_line)
        cmd = subprocess.Popen(args)
        cmd.wait()

        if cmd.returncode != 0:
            print("Failed to create container")
            self.destroy_libertine_container()
            return False

        # Remove symlinks as they can cause ill-behaved recursive behavior in the chroot
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
        if (self.architecture == 'armhf'):
            archive = "deb http://ports.ubuntu.com/ubuntu-ports "
        else:
            archive = "deb http://archive.ubuntu.com/ubuntu "

        if verbosity == 1:
            print("Updating chroot's sources.list entries...")
        with open(os.path.join(self.root_path, 'etc', 'apt', 'sources.list'), 'a') as fd:
            fd.write(archive + self.installed_release + "-updates main\n")
            fd.write(archive + self.installed_release + " universe\n")
            fd.write(archive + self.installed_release + "-updates universe\n")
            fd.write(archive + self.installed_release + " multiverse\n")
            fd.write(archive + self.installed_release + "-updates multiverse\n")

        utils.create_libertine_user_data_dir(self.container_id)

        if multiarch and self.architecture == 'amd64':
            if verbosity == 1:
                print("Adding i386 multiarch support...")
            self.run_in_container("dpkg --add-architecture i386")

        if verbosity == 1:
            print("Updating the contents of the container after creation...")
        self.update_packages(verbosity)

        for package in self.default_packages:
            if not self.install_package(package, verbosity, update_cache=False):
                print("Failure installing %s during container creation" % package)
                self.destroy_libertine_container()
                return False

        if self.installed_release == "vivid":
            if verbosity == 1:
                print("Installing the Vivid Stable Overlay PPA...")
            if not self.install_package("software-properties-common", verbosity, update_cache=False):
                print("Failure installing software-properties-common during container creation")
                self.destroy_libertine_container()
                return False

            self.run_in_container("add-apt-repository ppa:ci-train-ppa-service/stable-phone-overlay -y")
            self.update_packages(verbosity)

        # Check if the container was created as root and chown the user directories as necessary
        chown_recursive_dirs(utils.get_libertine_container_userdata_dir_path(self.container_id))

        return True

    def update_packages(self, verbosity=1):
        retcode = super().update_packages(verbosity)
        self._run_ldconfig(verbosity)
        return retcode

    def install_package(self, package_name, verbosity=1, no_dialog=False, update_cache=True):
        returncode = super().install_package(package_name, verbosity, no_dialog, update_cache)

        if returncode:
            self._run_ldconfig(verbosity)

        return returncode

    def _build_proot_command(self):
        proot_cmd = shutil.which('proot')
        if not proot_cmd:
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

        mounts = self._sanitize_bind_mounts(utils.get_common_xdg_user_directories() + \
                                            ContainersConfig().get_container_bind_mounts(self.container_id))
        for user_dir in utils.generate_binding_directories(mounts, home_path):
            user_dir_path = os.path.join(home_path, user_dir[1])
            bind_mounts += " -b %s:%s" % (user_dir[0], user_dir_path)

        proot_cmd += bind_mounts

        user_dconf_path = os.path.join(home_path, '.config', 'dconf')
        if os.path.exists(user_dconf_path):
            proot_cmd += " -b %s" % user_dconf_path

        return proot_cmd

    def _sanitize_bind_mounts(self, mounts):
        return [mount.replace(" ", "\\ ").replace("'", "\\'").replace('"', '\\"') for mount in mounts]

    def _build_privileged_proot_cmd(self):
        proot_cmd = shutil.which('proot')
        if not proot_cmd:
            raise RuntimeError('executable proot not found')

        proot_cmd += " -b /usr/lib/locale -S " + self.root_path

        return proot_cmd

    def start_application(self, app_exec_line, environ):
        # FIXME: Disabling seccomp is a temporary measure until we fully understand why we need
        #        it or figure out when we need it.
        environ['PROOT_NO_SECCOMP'] = '1'

        # Workaround issue where a custom dconf profile is on the machine
        if 'DCONF_PROFILE' in environ:
            del environ['DCONF_PROFILE']

        proot_cmd = self._build_proot_command()

        args = shlex.split(proot_cmd)
        args.extend(utils.setup_window_manager(self.container_id, enable_toolbars=True))
        window_manager = psutil.Popen(args, env=environ)

        args = shlex.split(proot_cmd)
        args.extend(app_exec_line)
        app = psutil.Popen(args, env=environ)
        return app

    def finish_application(self, app):
        utils.terminate_window_manager(window_manager)
        app.wait()

    def _run_ldconfig(self, verbosity=1):
        if verbosity == 1:
            print("Refreshing the container's dynamic linker run-time bindings...")

        command_line = self._build_privileged_proot_cmd() + " ldconfig.REAL"

        args = shlex.split(command_line)
        app = subprocess.Popen(args)
        return app

    def finish_application(self, app):
        app.wait()
