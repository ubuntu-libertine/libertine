/**
 * @file ContainerArchivesList.cpp
 * @brief Libertine Manager list of extra container archives, ie, PPAs
 */
/*
 * Copyright 2016-2017 Canonical Ltd
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
#include "common/ContainerArchivesList.h"

#include "common/ContainerConfigList.h"

ContainerArchivesList::
ContainerArchivesList(ContainerConfigList* container_config_list,
                      QObject* parent)
: QAbstractListModel(parent)
, container_config_list_(container_config_list)
{ }


void ContainerArchivesList::
setContainerArchives(QString const& container_id)
{
  archives_ = container_config_list_->getArchivesForContainer(container_id);

  beginResetModel();
  endResetModel();
}


bool ContainerArchivesList::
empty() const noexcept
{ return archives_.empty(); }


ContainerArchivesList::size_type ContainerArchivesList::
size() const noexcept
{ return archives_.count(); }


int ContainerArchivesList::
rowCount(QModelIndex const&) const
{
  return this->size();
}


QHash<int, QByteArray> ContainerArchivesList::
roleNames() const
{
  QHash<int, QByteArray> roles;
  roles[static_cast<int>(DataRole::ArchiveName)] = "archiveName";
  roles[static_cast<int>(DataRole::ArchiveStatus)] = "archiveStatus";

  return roles;
}


QVariant ContainerArchivesList::
data(QModelIndex const& index, int role) const
{
  QVariant result;

  if (index.isValid() && index.row() <= this->size())
  {
    switch (static_cast<DataRole>(role))
    {
      case DataRole::ArchiveName:
        result = archives_[index.row()].name;
        break;
      case DataRole::ArchiveStatus:
        result = archives_[index.row()].status;
        break;
      case DataRole::Error:
        break;
    }
  }

  return result;
}
