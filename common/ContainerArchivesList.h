/**
 * @file ContainerArchivesList.h
 * @brief Libertine Manager list of extra container archives (PPAs)
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
#pragma once

#include <QtCore/QAbstractListModel>
#include <QtCore/QList>
#include <QtCore/QObject>
#include <QtCore/QString>
#include "common/ContainersConfig.h"


class ContainerArchives;
class ContainerConfigList;

class ContainerArchivesList
: public QAbstractListModel
{
  Q_OBJECT

public:
  using ArchivesList = QList<ContainersConfig::Container::Archive>;
  using iterator = ArchivesList::iterator;
  using size_type = ArchivesList::size_type;

  enum class DataRole
  : int
  {
    ArchiveName = Qt::UserRole + 1,
    ArchiveStatus,
    Error
  };

public:
  explicit
  ContainerArchivesList(ContainerConfigList* container_config_list,
                        QObject* parent = nullptr);

  virtual
  ~ContainerArchivesList() = default;

  Q_INVOKABLE void
  setContainerArchives(QString const& container_id);

  Q_INVOKABLE bool
  empty() const noexcept;

  size_type
  size() const noexcept;

  int
  rowCount(QModelIndex const& parent = QModelIndex()) const;

  QHash<int, QByteArray>
  roleNames() const;

  QVariant
  data(QModelIndex const& index, int role = Qt::DisplayRole) const;

private:
  ContainerConfigList* container_config_list_;
  ArchivesList         archives_;
};
