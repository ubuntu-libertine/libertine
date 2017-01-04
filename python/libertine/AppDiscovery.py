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

from . import utils
from xdg.BaseDirectory import xdg_data_dirs
import configparser
import glob
import io
import json
import os
import re
import sys


class IconCache(object):
    """
    Caches the names of all icon files available in the standard places (possibly
    in a container) and provides a search function to deliver icon file names
    matching a given icon name.

    See the `Freedesktop.org icon theme specification
    <http://standards.freedesktop.org/icon-theme-spec/icon-theme-spec-latest.html>`_
    for the detailed specification.
    """

    def __init__(self, root_path, file_loader=None):
        """
        :param root_path: Where to start the file scan.
        :type root_path: A valid filesystem path string.
        :param file_loader: A function that builds a cache of filenames.
        :type file_loader: Function returning a list of filenames.
        """
        if file_loader:
            self._icon_cache = file_loader(root_path)
        else:
            self._icon_cache = self._file_loader(root_path)

    def _get_icon_search_paths(self, root_path):
        """
        Gets a list of paths on which to search for icons.

        :param root_path: Where to start the file scan.
        :type root_path: A valid filesystem path string.
        :rtype: A list of filesystem patch to serarch for qualifying icon files.
        """
        icon_search_paths = []
        icon_search_paths.append(os.path.join(root_path, os.environ['HOME'], ".icons"))
        for d in reversed(xdg_data_dirs):
            icon_search_paths.append(os.path.join(root_path, d.lstrip('/'), "icons"))
        icon_search_paths.append(os.path.join(root_path, "usr/share/pixmaps"))
        return icon_search_paths

    def _file_loader(self, root_path):
        """
        Loads a cache of file names by scanning the filesystem rooted at
        ``root_path``.

        :param root_path: Where to start the file scan.
        :type root_path: A valid filesystem path.
        :rtype: A list of fully-qualified file paths.
        """
        file_names = []
        pattern = re.compile(r".*\.(png|svg|xpm)")
        for path in self._get_icon_search_paths(root_path):
            for base, dirs, files in os.walk(path):
                for file in files:
                    if pattern.match(file):
                        file_names.append(os.path.join(base, file))
        return file_names

    def _find_icon_files(self, icon_name):
        """
        Finds a list of file name strings matching the given icon name.

        :param icon_name: An icon name, pobably from a .desktop file.
        :rtype: A list of filename strings matching the icon name.
        """
        icon_file_names = []
        match_string = r"/" + os.path.splitext(icon_name)[0] + r"\....$"
        pattern = re.compile(match_string)
        for icon_file in self._icon_cache:
            if pattern.search(icon_file):
                icon_file_names.append(icon_file)
        return icon_file_names

    def expand_icons(self, desktop_icon_list):
        """
        Expands a string containing a list of icon names into a list of matching
        file names.

        :param desktop_icon_list: A string containing a list of icon names
        separated by semicolons.
        :rtype: A list of filename stings matching the icon names passed in.

        See `the Freedesktop.org desktop file specification
        <http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html#recognized-keys>`_
        for more information.
        """
        if desktop_icon_list:
            icon_list = desktop_icon_list.split(';')
            if icon_list[0][0] == '/':
                return icon_list
            icon_files = []
            for i in icon_list:
                icon_files += self._find_icon_files(i)
            return icon_files
        return []


def expand_mime_types(desktop_mime_types):
    if desktop_mime_types:
        return desktop_mime_types.split(';')
    return []


class AppInfo(object):

    def __init__(self, desktop_file_name, config_entry, icon_cache):
        self.desktop_file_name = desktop_file_name
        self.name = config_entry.get('Name')
        if not self.name:
            raise RuntimeError("required Name attribute is missing")
        d = config_entry.get('NoDisplay')
        self.no_display = (d != None and d == 'true')
        self.exec_line = config_entry.get('Exec')
        if not self.exec_line:
            raise RuntimeError("required Exec attribute is missing")
        self.icons = icon_cache.expand_icons(config_entry.get('Icon'))
        self.mime_types = expand_mime_types(config_entry.get('MimeType'))

    def __str__(self):
        with io.StringIO() as ostr:
            print(self.name, file=ostr)
            print("  desktop_file={}".format(self.desktop_file_name), file=ostr)
            print("  no-display={}".format(self.no_display), file=ostr)
            print("  exec='{}'".format(self.exec_line), file=ostr)
            for icon in self.icons:
                print("  icon: {}".format(icon), file=ostr)
            for mime in self.mime_types:
                print("  mime: {}".format(mime), file=ostr)
            return ostr.getvalue()

    def to_json(self):
        return json.dumps(self.__dict__)


def desktop_file_is_showable(desktop_entry):
    """
    Determines if a particular application entry should be reported:  the entry
    can not be hidden and must be showable in Unity.
    """
    t = desktop_entry.get('Type')
    if t != 'Application':
        return False
    n = desktop_entry.get('Hidden')
    if n and n == 'true':
        return False
    n = desktop_entry.get('NoShowIn')
    if n:
        targets = n.split(';')
        if 'Unity' in targets:
            return False
    n = desktop_entry.get('OnlyShowIn')
    if n:
        targets = n.split(';')
        if 'Unity' not in targets:
            return False
    return True


def get_app_info(desktop_path, icon_cache):
    for desktop_file_name in glob.glob(desktop_path):
        desktop_file = configparser.ConfigParser(strict=False, interpolation=None)
        try:
            desktop_file.read(desktop_file_name)
            desktop_entry = desktop_file['Desktop Entry']
            if desktop_file_is_showable(desktop_entry):
                    yield AppInfo(desktop_file_name, desktop_entry, icon_cache)
        except Exception as ex:
            utils.get_logger().error("error processing {}: {}".format(desktop_file_name, ex))


class AppLauncherCache(object):
    """
    Caches a list of application launcher information (derived from .desktop
    files installed in a container.
    """

    def __init__(self, name, root_path):
        self.name = name
        self.app_launchers = []
        icon_cache = IconCache(root_path)
        for dir in reversed(xdg_data_dirs):
            path = os.path.join(root_path, dir.lstrip('/'), "applications")
            for app_info in get_app_info(os.path.join(path, "*.desktop"), icon_cache):
                self.app_launchers.append(app_info)

    def __str__(self):
        with io.StringIO() as ostr:
            print("{}\n".format(self.name), file=ostr)
            for app_info in self.app_launchers:
                print("  {}".format(app_info), file=ostr)
            return ostr.getvalue()

    def to_json(self):
        return json.dumps(self,
                          default=lambda o: o.__dict__,
                          sort_keys=True,
                          indent=4)
