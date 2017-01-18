/**
 * @file LibertineConfig.cpp
 * @brief Libertine Manager application-wide configuration module
 */
/*
 * Copyright 2015 Canonical Ltd
 *
 * Libertine is free software: you can redistribute it and/or modify it under
 * the terms of the GNU General Public License, version 3, as published by the
 * Free Software Foundation.
 *
 * Libertine is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
 * A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#include "common/LibertineConfig.h"

#include <cstdlib>
#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QStandardPaths>


QString LibertineConfig::
containers_config_file_name() const
{
  QString path = QStandardPaths::writableLocation(QStandardPaths::GenericDataLocation) + "/libertine";

  // if running from a snap
  auto snap_common = std::getenv("SNAP_USER_COMMON");
  if (snap_common != nullptr)
  {
    path.replace(std::getenv("HOME"), snap_common);
  }

  // if libertine is installed as a snap but caller is not;
  // workaround until ContainersConfig is only discovered from one location
  if (QString(std::getenv("IGNORE_SNAP")) != "1" && QFile::exists("/snap/bin/libertine.libertine-launch"))
  {
    auto home = std::getenv("HOME");
    path.replace(home, QString(home) + "/snap/libertine/common");
  }

  QDir dir(path);

  if (!dir.exists())
  {
    dir.mkpath(path);
  }

  QString file_name = path + "/ContainersConfig.json";

  if (!QFile::exists(file_name))
  {
    QFile file(file_name);
    file.open(QIODevice::WriteOnly);
    file.close();
  }

  return file_name;
}
