/**
 * @file LibertineConfig.cpp
 * @brief Libertine Manager application-wide configuration module
 */
/*
 * Copyright 2015-2016 Canonical Ltd
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
#ifndef LIBERTINE_LIBERTINECONFIG_H
#define LIBERTINE_LIBERTINECONFIG_H

#include <QtCore/QString>


/**
 * The runtime configuration of the Libertine tools.
 */
class LibertineConfig
{
public:
  explicit LibertineConfig() = default;
  virtual ~LibertineConfig() = default;

  QString
  containers_config_file_name() const;
};

#endif /* LIBERTINE_LIBERTINECONFIG_H */
