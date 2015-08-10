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

import lxc
import subprocess
import os
import lsb_release
import crypt
import ctypes
import tempfile
import io
import sys
import shlex
import shutil
import xdg.BaseDirectory as basedir

from contextlib import contextmanager

home_path = os.environ['HOME']

libc = ctypes.CDLL(None)
c_stdout = ctypes.c_void_p.in_dll(libc, 'stdout')

@contextmanager
def output_redirector(stream):
    # The original fd stdout points to. Usually 1 on POSIX systems.
    original_stdout_fd = sys.stdout.fileno()
    original_stderr_fd = sys.stderr.fileno()

    def _redirect_output(to_fd):
        """Redirect stdout/stderr to the given file descriptor."""
        # Flush the C-level buffer stdout
        libc.fflush(c_stdout)
        # Flush and close sys.stdout/sys.stderr - also closes the file descriptor (fd)
        sys.stdout.close()
        sys.stderr.close()
        # Make original_stdout_fd point to the same file as to_fd
        os.dup2(to_fd, original_stdout_fd)
        # Create a new sys.stdout that points to the redirected fd
        sys.stdout = io.TextIOWrapper(os.fdopen(original_stdout_fd, 'wb'))

        # Make original_stderr_fd point to sys.stdout fd
        os.dup2(sys.stdout.fileno(), original_stderr_fd)
        # Create a new sys.stderr that points to the redirected fd
        sys.stderr = io.TextIOWrapper(os.fdopen(original_stderr_fd, 'wb'))

    def _restore_output(stdout_fd, stderr_fd):
        libc.fflush(c_stdout)

        sys.stdout.close()
        sys.stderr.close()

        os.dup2(stdout_fd, original_stdout_fd)
        os.dup2(stderr_fd, original_stderr_fd)

        sys.stdout = io.TextIOWrapper(os.fdopen(original_stdout_fd, 'wb'))
        sys.stderr = io.TextIOWrapper(os.fdopen(original_stderr_fd, 'wb'))

    # Save a copy of the original stdout fd in saved_stdout_fd
    saved_stdout_fd = os.dup(original_stdout_fd)
    saved_stderr_fd = os.dup(original_stderr_fd)
    try:
        # Create a temporary file and redirect stdout to it
        tfile = tempfile.TemporaryFile(mode='w+b')
        _redirect_output(tfile.fileno())
        # Yield to caller, then redirect stdout back to the saved fd
        yield
        _restore_output(saved_stdout_fd, saved_stderr_fd)
        # Copy contents of temporary file to the given stream
        tfile.flush()
        tfile.seek(0, io.SEEK_SET)
        stream.write(tfile.read())
    finally:
        tfile.close()
        os.close(saved_stdout_fd)
        os.close(saved_stderr_fd)

def check_lxc_net_entry(entry):
    lxc_net_file = open('/etc/lxc/lxc-usernet')
    found = False

    for line in lxc_net_file:
        if entry in line:
            found = True
            break

    return found

def setup_host_environment(username, password):
    lxc_net_entry = "%s veth lxcbr0 10" % str(username)

    if not check_lxc_net_entry(lxc_net_entry):
        dev_null = open('/dev/null', 'w')
        passwd = subprocess.Popen(["sudo", "--stdin", "usermod", "--add-subuids", "100000-165536",
                                   "--add-subgids", "100000-165536", str(username)], stdin=subprocess.PIPE,
                                  stdout=dev_null.fileno(), stderr=subprocess.STDOUT)
        passwd.communicate((password + '\n').encode('UTF-8'))
        dev_null.close()

        add_user_cmd = "echo %s | sudo tee -a /etc/lxc/lxc-usernet > /dev/null" % lxc_net_entry
        subprocess.Popen(add_user_cmd, shell=True)

def get_host_distro_release():
    distinfo = lsb_release.get_distro_information()

    return distinfo.get('CODENAME', 'n/a')

def get_libertine_container_path():
    return basedir.save_cache_path('libertine-container')

def get_lxc_default_config_path():
    return os.path.join(home_path, '.config', 'lxc')

def get_libertine_user_data_dir(name):
    return os.path.join(basedir.xdg_data_home, 'libertine-container', 'user-data', name)

def create_libertine_user_data_dir(name):
    user_data = get_libertine_user_data_dir(name)

    if not os.path.exists(user_data):
        os.makedirs(user_data)

def start_container_for_update(container):
    if not container.running:
        print("Starting the container...")
        if not container.start():
            print("Container failed to start")
            return False
        if not container.wait("RUNNING", 10):
            print("Container failed to enter the RUNNING state")
            return False

    if not container.get_ips(timeout=30):
        print("Not able to connect to the network.")
        return False

    container.attach_wait(lxc.attach_run_command,
                          ["umount", "/tmp/.X11-unix"])

    container.attach_wait(lxc.attach_run_command,
                          ["apt-get", "update"])

    return True

def lxc_container(name):
    config_path = get_libertine_container_path()
    container = lxc.Container(name, config_path)

    return container

def list_libertine_containers():
    containers = lxc.list_containers(config_path=get_libertine_container_path())

    return containers

class LibertineLXC(object):
    def __init__(self, name):
        self.container = lxc_container(name)

    def destroy_libertine_container(self):
        if self.container.defined:
            self.container.stop()
            self.container.destroy()

    def create_libertine_container(self, password=None):
        if password is None:
            return

        username = os.environ['USER']
        user_id = os.getuid()
        group_id = os.getgid()

        setup_host_environment(username, password)

        # Generate the default lxc default config, if it doesn't exist
        config_path = get_lxc_default_config_path()
        config_file = "%s/default.conf" % config_path

        if not os.path.exists(config_path):
            os.mkdir(config_path)

        if not os.path.exists(config_file):
            with open(config_file, "w+") as fd:
                fd.write("lxc.network.type = veth\n")
                fd.write("lxc.network.link = lxcbr0\n")
                fd.write("lxc.network.flags = up\n")
                fd.write("lxc.network.hwaddr = 00:16:3e:xx:xx:xx\n")
                fd.write("lxc.id_map = u 0 100000 %s\n" % user_id)
                fd.write("lxc.id_map = g 0 100000 %s\n" % group_id)
                fd.write("lxc.id_map = u %s %s 1\n" % (user_id, user_id))
                fd.write("lxc.id_map = g %s %s 1\n" % (group_id, group_id))
                fd.write("lxc.id_map = u %s %s %s\n" % (user_id + 1, (user_id + 1) + 100000, 65536 - (user_id + 1)))
                fd.write("lxc.id_map = g %s %s %s\n" % (group_id + 1, (group_id + 1) + 100000, 65536 - (user_id + 1)))
            fd.close()

        create_libertine_user_data_dir(self.container.name)

        ## Get to the codename of the host Ubuntu release so container will match
        installed_release = get_host_distro_release()

        ## Figure out the host architecture
        dpkg = subprocess.Popen(['dpkg', '--print-architecture'],
                                stdout=subprocess.PIPE,
                                universal_newlines=True)
        if dpkg.wait() != 0:
            parser.error("Failed to determine the local architecture.")

        architecture = dpkg.stdout.read().strip()

        self.container.create("download", 0,
                              {"dist": "ubuntu",
                               "release": installed_release,
                               "arch": architecture})

        self.create_libertine_config()

        if self.container.start():
            self.container.attach_wait(lxc.attach_run_command,
                                       ["userdel", "-r", "ubuntu"])

            self.container.attach_wait(lxc.attach_run_command,
                                       ["useradd", "-u", str(user_id), "-p", crypt.crypt(password),
                                        "-G", "sudo", str(username)])

            self.container.stop()
        else:
            print("Container failed to start.")

    def create_libertine_config(self):
        user_id = os.getuid()
        home_entry = "%s %s none bind,create=dir" % (get_libertine_user_data_dir(self.container.name), home_path.strip('/'))

        # Bind mount the user's home directory
        self.container.append_config_item("lxc.mount.entry", home_entry)

        xdg_user_dirs = ['Documents', 'Music', 'Pictures', 'Videos']

        for user_dir in xdg_user_dirs:
            xdg_user_dir_entry = "%s/%s %s/%s none bind,create=dir,optional" % (home_path, user_dir, home_path.strip('/'), user_dir)
            self.container.append_config_item("lxc.mount.entry", xdg_user_dir_entry)

        # Bind mount the X socket directories
        self.container.append_config_item("lxc.mount.entry", "/tmp/.X11-unix tmp/.X11-unix/ none bind,create=dir")

        # Setup the mounts for /run/user/$user_id
        run_user_entry = "/run/user/%s run/user/%s none rbind,create=dir" % (user_id, user_id)
        self.container.append_config_item("lxc.mount.entry", "tmpfs run tmpfs rw,nodev,noexec,nosuid,size=5242880")
        self.container.append_config_item("lxc.mount.entry", "none run/user tmpfs rw,nodev,noexec,nosuid,size=104857600,mode=0755,create=dir")
        self.container.append_config_item("lxc.mount.entry", run_user_entry)

        # No tty's to work around an issue when using this from a GUI
        self.container.clear_config_item("lxc.tty")
        self.container.set_config_item("lxc.tty", "0")

        ## Dump it all to disk
        self.container.save_config()

    def update_libertine_container(self):
        # Update packages inside the LXC
        start_container_for_update(self.container)

        print("Updating packages inside the LXC...")

        self.container.attach_wait(lxc.attach_run_command,
                                   ["apt-get", "dist-upgrade", "-y"])

        ## Stopping the container
        self.container.stop()

    def install_package(self, package_name):
        f = io.BytesIO()
        stop_container = False

        if not self.container.running:
            if not start_container_for_update(self.container):
              return (False, "Container did not start")
            stop_container = True

        with output_redirector(f):
            retval = self.container.attach_wait(lxc.attach_run_command,
                                                ["apt-get", "install", "-y", "--no-install-recommends", package_name])

        if stop_container:
            self.container.stop()

        if retval != 0:
            lxc_output = f.getvalue().split(b'\n')

            for line in lxc_output:
                if line.decode().startswith('E: '):
                    return (False, line.decode().lstrip('E: '))

        return True

    def remove_package(self, package_name):
        f = io.BytesIO()
        stop_container = False

        if not self.container.running:
            if not start_container_for_update(self.container):
              return (False, "Container did not start")
            stop_container = True

        with output_redirector(f):
            retval = self.container.attach_wait(lxc.attach_run_command,
                                                ["apt-get", "remove", "-y", package_name])

        if stop_container:
            self.container.stop()


class LibertineChroot(object):
    def __init__(self, name):
        self.name = name
        self.chroot_path = os.path.join(get_libertine_container_path(), name, "rootfs")
        os.environ['FAKECHROOT_CMD_SUBST'] = '$FAKECHROOT_CMD_SUBST:/usr/bin/chfn=/bin/true'

    def destroy_libertine_container(self):
        shutil.rmtree(self.chroot_path)

    def create_libertine_container(self, password=None):
        installed_release = get_host_distro_release()

        # Create the actual chroot
        command_line = "fakechroot fakeroot debootstrap --verbose --variant=fakechroot " + installed_release + " " + self.chroot_path
        args = shlex.split(command_line)
        subprocess.Popen(args).wait()

        # Remove symlinks as they can ill-behaved recursive behavior in the chroot
        print("Fixing chroot symlinks...")
        os.remove(os.path.join(self.chroot_path, 'dev'))
        os.remove(os.path.join(self.chroot_path, 'proc'))

        # Add universe and -updates to the chroot's sources.list
        print("Updating chroot's sources.list entries...")
        with open(os.path.join(self.chroot_path, 'etc', 'apt', 'sources.list'), 'a') as fd:
            fd.write("deb http://archive.ubuntu.com/ubuntu " + installed_release + " universe\n")
            fd.write("deb http://archive.ubuntu.com/ubuntu " + installed_release + "-updates main\n")
            fd.write("deb http://archive.ubuntu.com/ubuntu " + installed_release + "-updates universe\n")

            fd.close()

        # Generate the proper locale(s) in the chroot
        print("Generating chroot's locale...")
        locale = os.popen("locale", "r").read().split("\n")
        locales = ''

        for line in locale:
            if line == "":
                break
            line = line.split('=')[1].replace("\"", "")
            if not line in locales and line != "":
                locales += ' ' + line

        command_line = "fakechroot fakeroot chroot " + self.chroot_path + " /usr/sbin/locale-gen " + locales
        args = shlex.split(command_line)
        cmd = subprocess.Popen(args).wait()

    def update_libertine_container(self):
        command_line = "fakechroot fakeroot chroot " + self.chroot_path + " /usr/bin/apt-get update"
        args = shlex.split(command_line)
        cmd = subprocess.Popen(args).wait()

        command_line = "fakechroot fakeroot chroot " + self.chroot_path + " /usr/bin/apt-get dist-upgrade -y"
        args = shlex.split(command_line)
        cmd = subprocess.Popen(args).wait()

    def install_package(self, package_name):
        command_line = "fakechroot fakeroot chroot " + self.chroot_path + " /usr/bin/apt-get install -y " + package_name
        args = shlex.split(command_line)
        cmd = subprocess.Popen(args).wait()

    def remove_package(self, package_name):
        command_line = "fakechroot fakeroot chroot " + self.chroot_path + " /usr/bin/apt-get remove -y " + package_name
        args = shlex.split(command_line)
        cmd = subprocess.Popen(args).wait()

class LibertineContainer(object):
    """
    A sandbox for DEB-packaged X11-based applications.
    """
    def __init__(self, name, container_type="lxc"):
        super().__init__()
        if container_type == "lxc":
            self.container = LibertineLXC(name)

        elif container_type == "chroot":
            self.container = LibertineChroot(name)

        else:
            print("Unsupported container type %s" % container_type)

    def destroy_libertine_container(self):
        self.container.destroy_libertine_container()

    def create_libertine_container(self, password=None):
        self.container.create_libertine_container(password)

    def create_libertine_config(self):
        self.container.create_libertine_config()

    def update_libertine_container(self):
        self.container.update_libertine_container()

    def install_package(self, package_name):
        self.container.install_package(package_name)

    def remove_package(self, package_name):
        self.container.remove_package(package_name)
