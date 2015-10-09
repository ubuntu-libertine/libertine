/**
 * @file ContainerAppsList.h
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
#ifndef _CONTAINER_APPS_LIST_H_
#define _CONTAINER_APPS_LIST_H_

#include "libertine/ContainerConfig.h"

#include <QtCore/QAbstractListModel>
#include <QtCore/QList>
#include <QtCore/QObject>
#include <QtCore/QString>


class ContainerApps;
class ContainerConfigList;

class ContainerAppsList
: public QAbstractListModel
{
  Q_OBJECT

public:
  using AppsList = QList<ContainerApps*>;
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

  ~ContainerAppsList();

  Q_INVOKABLE void
  setContainerApps(QString const& container_id);

  Q_INVOKABLE void
  addNewApp(QString const& container_id, QString const& package_name);

  Q_INVOKABLE void
  removeApp(QString const& container_id, QString const& package_name);

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
  AppsList*            apps_;
};

#endif /* _CONTAINER_APPS_LIST_H_ */
