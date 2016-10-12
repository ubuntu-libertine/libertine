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

#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QStandardPaths>


QString LibertineConfig::
containers_config_file_name() const
{
  QString path = QStandardPaths::writableLocation(QStandardPaths::GenericDataLocation) + "/libertine";
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
