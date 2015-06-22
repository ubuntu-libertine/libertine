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
#include "libertine/LibertineConfig.h"

#include "libertine/libertine.h"
#include <QtCore/QCommandLineParser>
#include <QtCore/QStandardPaths>


LibertineConfig::
LibertineConfig(Libertine const& libertine)
{
  QCommandLineParser commandlineParser;
  commandlineParser.setApplicationDescription("manage sandboxes for running legacy DEB-packaged X11-based applications");
  commandlineParser.addHelpOption();
  commandlineParser.addVersionOption();
  commandlineParser.process(libertine);
}


LibertineConfig::
LibertineConfig()
{
}


LibertineConfig::
~LibertineConfig()
{
}


QString LibertineConfig::
containers_config_file_name() const
{
  QString path = QStandardPaths::writableLocation(QStandardPaths::DataLocation);
  QString file_name = path + "/ContainersConfig.json";
  return file_name;
}

