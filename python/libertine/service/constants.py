# Copyright 2017 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

SERVICE_NAME                 = "com.canonical.libertine.Service"

OPERATIONS_INTERFACE         = "com.canonical.libertine.Service.Operations"
OPERATIONS_OBJECT            = "/com/canonical/libertine/Service/Operations"

DOWNLOAD_INTERFACE           = "com.canonical.applications.Service.Download"
DOWNLOAD_OBJECT              = "/com/canonical/libertine/Service/Download/%s"

OPERATIONS_MONITOR_INTERFACE = "com.canonical.libertine.Service.OperationsMonitor"
OPERATIONS_MONITOR_OBJECT    = "/com/canonical/libertine/Service/OperationsMonitor"

CONTAINER_CONTROL_INTERFACE  = "com.canonical.libertine.Service.ContainerControl"
CONTAINER_CONTROL_OBJECT     = "/com/canonical/libertine/Service/ContainerControl"
