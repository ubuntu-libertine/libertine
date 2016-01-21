/**
 * @file ContainerAppsList.cpp
 * @brief Libertine Manager list of container applications
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
#include "libertine/ContainerAppsList.h"
#include "libertine/ContainerConfigList.h"

ContainerAppsList::
ContainerAppsList(ContainerConfigList* container_config_list,
                  QObject* parent)
: QAbstractListModel(parent)
, container_config_list_(container_config_list)
{ }


ContainerAppsList::
~ContainerAppsList()
{ }


void ContainerAppsList::
setContainerApps(QString const& container_id)
{
  apps_ = container_config_list_->getAppsForContainer(container_id);
}


void ContainerAppsList::
addNewApp(QString const& container_id, QString const& package_name)
{
  container_config_list_->addNewApp(container_id, package_name);

  beginResetModel();
  endResetModel();
}


void ContainerAppsList::
removeApp()
{
  beginResetModel();
  endResetModel();
}


bool ContainerAppsList::
empty() const noexcept
{ return apps_->empty(); }


ContainerAppsList::size_type ContainerAppsList::
size() const noexcept
{ return apps_->count(); }


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

  if (index.isValid() && index.row() <= apps_->count())
  {
    switch (static_cast<DataRole>(role))
    {
      case DataRole::PackageName:
        result = (*apps_)[index.row()]->package_name();
        break;
      case DataRole::AppStatus:
        result = (*apps_)[index.row()]->app_status();
        break;
      case DataRole::Error:
        break;
    }
  }

  return result;
}
