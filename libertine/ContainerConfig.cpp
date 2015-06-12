/**
 * @file ContainerConfig.cpp
 * @brief Libertine Manager containers configuration module
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
#include "libertine/ContainerConfig.h"


ContainerConfig::
ContainerConfig(QObject* parent)
: QObject(parent)
{ }


ContainerConfig::
ContainerConfig(QString const& container_id,
                QString const& container_name,
                QString const& image_id,
                QObject*       parent)
: QObject(parent)
, container_id_(container_id)
, container_name_(container_name)
, image_id_(image_id)
, install_status_(InstallStatus::New)
{ }


ContainerConfig::
~ContainerConfig()
{ }


QString const& ContainerConfig::
container_id() const
{ return container_id_; }


QString const& ContainerConfig::
name() const
{ return container_name_; }


void ContainerConfig::
name(QString const& name)
{
  container_name_ = name;
  emit nameChanged();
}


QString const& ContainerConfig::
image_id() const
{ return image_id_; }


ContainerConfig::InstallStatus ContainerConfig::
install_status() const
{ return install_status_; }


void ContainerConfig::
install_status(InstallStatus install_status)
{
  install_status_ = install_status;
  emit installStatusChanged();
}

