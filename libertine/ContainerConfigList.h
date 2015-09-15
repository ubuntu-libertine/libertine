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

#include "libertine/libertine_lxc_manager_wrapper.h"

#include <QtCore/QAbstractListModel>
#include <QtCore/QJsonObject>
#include <QtCore/QList>


class ContainerApps;
class ContainerConfig;
class LibertineConfig;


/**
 * The runtime configuration of the Libertine tools.
 */
class ContainerConfigList
: public QAbstractListModel
{
  Q_OBJECT

  Q_PROPERTY(QString defaultContainerId
             READ default_container_id
             WRITE default_container_id
             NOTIFY defaultContainerChanged)

public:
  using ConfigList = QList<ContainerConfig*>;
  using iterator = ConfigList::iterator;
  using size_type = ConfigList::size_type;

  static const QString Json_container_list;
  static const QString Json_default_container;

  /**
   * Display roles for a container config.
   */
  enum class DataRole
  : int
  {
    ContainerId = Qt::UserRole + 1,   /**< The container ID */
    ContainerName,                    /**< The container name */
    ContainerType,                    /**< The type of container - lxc or chroot */
    DistroSeries,                     /**< The distro from which the container was built */
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
   * Constructs a container config list from a container config.
   */
  ContainerConfigList(LibertineConfig const* config,
                      QObject*               parent = nullptr);

  /**
   * Tears dow the container config list.
   */
  ~ContainerConfigList();

  Q_INVOKABLE QString
  addNewContainer(QVariantMap const& image, QString const& type);

  Q_INVOKABLE bool
  deleteContainer(QString const& container_id);

  Q_INVOKABLE void
  addNewApp(QString const& container_id,
            QString const& package_name);

  void
  removeApp(QString const& container_id,
            int index);

  QList<ContainerApps*> *
  getAppsForContainer(QString const& container_id);

  Q_INVOKABLE bool
  isAppInstalled(QString const& container_id,
                 QString const& package_name);

  int
  getAppIndex(QString const& container_id,
              QString const& package_name);

  Q_INVOKABLE QString
  getContainerType(QString const& container_id);

  QJsonObject
  toJson() const;

  QString const&
  default_container_id() const;

  void
  default_container_id(QString const& container_id);

  /**
   * @addtogroup Standard container interface
   * @{
   */
  /**
   * Indicates if the list of available containers is empty.
   */
  Q_INVOKABLE bool
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

signals:
  void
  defaultContainerChanged();

private:
  /**
   * Generates a bis (suffix) that can be used to distinguish between otherwise
   * identical container ids and names.
   */
  int
  generate_bis(QString const& distro_series);

  void
  save_container_config_list();

  int
  getContainerIndex(QString const& container_id);

private:
  LibertineConfig const* config_;
  ConfigList             configs_;
  QString                default_container_id_;
};

#endif /* CONTAINER_CONTAINERCONFIGLIST_H */
