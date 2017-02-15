/**
 * @file ContainerAppsList.cpp
 * @brief Libertine Manager list of container applications
 */
/*
 * Copyright 2015-2017 Canonical Ltd
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
#include "common/ContainerAppsList.h"

#include "common/ContainerConfigList.h"

ContainerAppsList::
ContainerAppsList(ContainerConfigList* container_config_list,
                  QObject* parent)
: QAbstractListModel(parent)
, container_config_list_(container_config_list)
{ }


void ContainerAppsList::
setContainerApps(QString const& container_id)
{
  apps_ = container_config_list_->getAppsForContainer(container_id);
  reloadAppsList();
}


void ContainerAppsList::
reloadAppsList()
{
  beginResetModel();
  endResetModel();
}


bool ContainerAppsList::
empty() const noexcept
{ return apps_.empty(); }


ContainerAppsList::size_type ContainerAppsList::
size() const noexcept
{ return apps_.count();}


int ContainerAppsList::
rowCount(QModelIndex const&) const
{
  return this->size();
}


QHash<int, QByteArray> ContainerAppsList::
roleNames() const
{
  QHash<int, QByteArray> roles;
  roles[static_cast<int>(DataRole::PackageName)] = "packageName";
  roles[static_cast<int>(DataRole::AppStatus)]   = "appStatus";
  return roles;
}


QVariant ContainerAppsList::
data(QModelIndex const& index, int role) const
{
  QVariant result;

  if (index.isValid() && index.row() <= size())
  {
    switch (static_cast<DataRole>(role))
    {
      case DataRole::PackageName:
        result = apps_[index.row()].name;
        break;
      case DataRole::AppStatus:
        result = apps_[index.row()].status;
        break;
      case DataRole::Error:
        break;
    }
  }

  return result;
}
