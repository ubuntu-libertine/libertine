/**
 * @file ContainerBindMountsList.cpp
 * @brief Libertine Manager list of all mapped directories
 */
/*
 * Copyright 2017 Canonical Ltd
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
#include "common/ContainerBindMountsList.h"

#include "common/ContainerConfigList.h"


ContainerBindMountsList::
ContainerBindMountsList(ContainerConfigList* container_config_list,
                      QObject* parent)
: QAbstractListModel(parent)
, container_config_list_(container_config_list)
{ }


void ContainerBindMountsList::
setContainerBindMounts(QString const& container_id)
{
  mounts_ = container_config_list_->getBindMountsForContainer(container_id);

  beginResetModel();
  endResetModel();
}


bool ContainerBindMountsList::
empty() const noexcept
{ return mounts_.empty(); }


ContainerBindMountsList::size_type ContainerBindMountsList::
size() const noexcept
{ return mounts_.count(); }


int ContainerBindMountsList::
rowCount(QModelIndex const&) const
{
  return this->size();
}


QHash<int, QByteArray> ContainerBindMountsList::
roleNames() const
{
  QHash<int, QByteArray> roles;
  roles[static_cast<int>(DataRole::BindMountPath)] = "path";

  return roles;
}


QVariant ContainerBindMountsList::
data(QModelIndex const& index, int role) const
{
  QVariant result;

  if (index.isValid() && index.row() <= mounts_.count())
  {
    switch (static_cast<DataRole>(role))
    {
      case DataRole::BindMountPath:
        result = mounts_[index.row()].path;
        break;
      case DataRole::Error:
        break;
    }
  }

  return result;
}
