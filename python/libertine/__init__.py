"""
:mod:`libertine` -- bindings for the Libertine application sandbox
==================================================================

.. module:: libertine
   :synopsis: A sandbox for running DEB-packaged X11-based applications
"""

# Copyright 2015-2017 Canonical Ltd.
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

__all__ = [
          # from Libertine
          'ContainerRunning',
          'LibertineContainer',
          'NoContainer',
          'utils',
          ]

__docformat__ = "restructuredtext en"

from libertine.Libertine import ContainerRunning, LibertineContainer, NoContainer
