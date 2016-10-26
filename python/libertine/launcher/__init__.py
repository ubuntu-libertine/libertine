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

"""Provides the Libertine launcher functionality.

All the things used specifically for launching and running an application under
a Libertine aegis are in this subpackage.  It is the principal guts of the
libertine-launch tool and associated test suites.

This is the public interface of the Libertine launcher package.
"""

from .config import Config, SocketBridge
from .session import Session, translate_to_real_address
from .task import LaunchServiceTask, TaskConfig, TaskType

__all__ = ('Config', 'Session')
