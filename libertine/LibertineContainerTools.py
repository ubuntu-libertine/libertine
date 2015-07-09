# LibertineContainerTools.py

import lxc
import subprocess
import os
import lsb_release
import crypt

home_path = os.environ['HOME']

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

def get_libertine_container_path():
    path = "%s/.cache/libertine-container/" % home_path

    return path

def get_libertine_user_data_dir(name):
    user_data_path = "%s/.local/share/libertine-container/user-data/%s" % (home_path, name)

    return user_data_path

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

def instantiate_libertine_container(name):
    config_path = get_libertine_container_path()
    container = lxc.Container(name, config_path)

    return container

def list_libertine_containers():
    containers = lxc.list_containers(config_path=get_libertine_container_path())

    return containers

class LibertineContainer():
    def __init__(self, name):
         self.container = instantiate_libertine_container(name)

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
        config_path = get_libertine_container_path()
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
        distinfo = lsb_release.get_distro_information()
        installed_release = distinfo.get('CODENAME', 'n/a')

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
        stop_container = False

        if not self.container.running:
            if not start_container_for_update(self.container):
              return (False, "Container did not start")
            stop_container = True

        self.container.attach_wait(lxc.attach_run_command,
                                   ["apt-get", "install", "-y", "--no-install-recommends", package_name])

        if stop_container:
            self.container.stop()

        return True
