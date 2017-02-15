/**
 * @file ContainerAppsList.h
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
#pragma once

#include <QtCore/QAbstractListModel>
#include <QtCore/QList>
#include <QtCore/QObject>
#include <QtCore/QString>
#include "common/ContainersConfig.h"


class ContainerConfigList;


class ContainerAppsList
: public QAbstractListModel
{
  Q_OBJECT

public:
  using AppsList = QList<ContainersConfig::Container::InstalledApp>;
  using iterator = AppsList::iterator;
  using size_type = AppsList::size_type;

  enum class DataRole
  : int
  {
    PackageName = Qt::UserRole + 1,
    AppStatus,
    Error
  };

public:
  explicit
  ContainerAppsList(ContainerConfigList* container_config_list,
                    QObject* parent = nullptr);

  virtual
  ~ContainerAppsList() = default;

  Q_INVOKABLE void
  setContainerApps(QString const& container_id);

  Q_INVOKABLE void
  reloadAppsList();

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
  AppsList             apps_;
};
