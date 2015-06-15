/**
 * @file ContainerConfigList.h
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
#ifndef CONTAINER_CONTAINERCONFIGLIST_H
#define CONTAINER_CONTAINERCONFIGLIST_H

#include <QtCore/QAbstractListModel>
#include <QtCore/QJsonObject>
#include <QtCore/QList>


class ContainerConfig;


/**
 * The runtime configuration of the Libertine tools.
 */
class ContainerConfigList
: public QAbstractListModel
{
  Q_OBJECT

public:
  using ConfigList = QList<ContainerConfig*>;
  using iterator = ConfigList::iterator;
  using size_type = ConfigList::size_type;

  static const QString Json_object_name;

  /**
   * Display roles for a container config.
   */
  enum class DataRole
  : int
  {
    ContainerId = Qt::UserRole + 1,   /**< The container ID */
    ContainerName,                    /**< The container name */
    ImageId,                          /**< The image from which the container was built */
    InstallStatus,                    /**< Current container install status */
    Error                             /**< last role (error) */
  };

public:
  /**
   * Constructs a default-initialized (empty) list.
   */
  explicit
  ContainerConfigList(QObject* parent = nullptr);

  /**
   * Constructs a container config list from an (in-memory) JSON string.
   */
  ContainerConfigList(QJsonObject const& json_object,
                      QObject*           parent = nullptr);

  /**
   * Tears dow the container config list.
   */
  ~ContainerConfigList();

  /** 
   * @addtogroup Standard container interface
   * @{
   */
  /**
   * Indicates if the list of available containers is empty.
   */
  bool
  empty() const noexcept;

  /**
   * Gets the number of container configs in the list.
   */
  size_type
  size() const noexcept;

  /** @} */

  /** 
   * @addtogroup QML interface
   * @{
   */
  /**
   * Gets the number of rows in the data model.
   */
  int
  rowCount(QModelIndex const& parent = QModelIndex()) const;

  /**
   * Gets the names of the various display roles.
   */
  QHash<int, QByteArray>
  roleNames() const;
  
  /**
   * Gets the column data for a row by role.
   */
  QVariant
  data(QModelIndex const& index, int role = Qt::DisplayRole) const;

  /** @} */

private:
  ConfigList configs_;
};

#endif /* CONTAINER_CONTAINERCONFIGLIST_H */
