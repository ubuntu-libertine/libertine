/**
 * @file ContainerConfigList.cpp
 * @brief Libertine Manager list of containers configurations
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
#include "libertine/ContainerConfigList.h"

#include "libertine/ContainerConfig.h"
#include <QtCore/QJsonArray>
#include <QtCore/QJsonObject>
#include <QtCore/QJsonValue>

const QString ContainerConfigList::Json_object_name = "containerConfigs";


ContainerConfigList::
ContainerConfigList(QObject* parent)
: QObject(parent)
{ }


ContainerConfigList::
ContainerConfigList(QJsonObject const& json_object,
                    QObject*           parent)
: QObject(parent)
{
  if (!json_object.empty())
  {
    QJsonArray containerConfigs = json_object[Json_object_name].toArray();
    for (auto const& config: containerConfigs)
    {
      QJsonObject containerConfig = config.toObject();
      configs_.append(new ContainerConfig(containerConfig, this));
    }
  }
}


ContainerConfigList::
~ContainerConfigList()
{ }


bool ContainerConfigList::
empty() const noexcept
{
  return configs_.empty();
}


ContainerConfigList::size_type ContainerConfigList::
size() const noexcept
{
  return configs_.count();
}

