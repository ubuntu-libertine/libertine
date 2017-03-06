/**
 * @file ContainerConfigList.h
 * @brief Libertine Manager list of containers configurations
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


#include "common/ContainersConfig.h"
#include <memory>
#include <QtCore/QAbstractListModel>
#include <QtCore/QJsonObject>
#include <QtCore/QList>


class ContainerApps;
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
  using size_type = QList<ContainersConfig::Container>::size_type;

  static const QString Json_container_list;
  static const QString Json_default_container;

  /**
   * Display roles for a container config.
   */
  enum class DataRole
  {
    ContainerId = Qt::UserRole + 1,   /**< The container ID */
    ContainerName,                    /**< The container name */
    ContainerType,                    /**< The type of container */
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
   * Constructs a container config list from a container config.
   */
  explicit
  ContainerConfigList(LibertineConfig const* config,
                      QObject*               parent = nullptr);

  /**
   * Constructs a container config list from a raw json string
   */
  explicit
  ContainerConfigList(QJsonObject const& json_object,
                      QObject*               parent = nullptr);

  /**
   * Tears down the container config list.
   */
  virtual ~ContainerConfigList() = default;

  Q_INVOKABLE void
  reloadContainerList();

  Q_INVOKABLE QString
  addNewContainer(QString const& type,
                  QString name);

  Q_INVOKABLE void
  deleteContainer();

  QList<ContainersConfig::Container::InstalledApp>
  getAppsForContainer(QString const& container_id);

  Q_INVOKABLE bool
  isAppInstalled(QString const& container_id,
                 QString const& package_name);

  Q_INVOKABLE QString
  getAppStatus(QString const& container_id,
               QString const& package_name);

  Q_INVOKABLE QString
  getAppVersion(QString const& app_info, bool installed);

  Q_INVOKABLE bool
  isValidDebianPackage(QString const& package_string);

  Q_INVOKABLE QString
  getDebianPackageName(QString const& package_path);

  Q_INVOKABLE QString
  getDownloadsLocation();

  Q_INVOKABLE QStringList
  getDebianPackageFiles();

  QList<ContainersConfig::Container::Archive>
  getArchivesForContainer(QString const& container_id);

  QList<ContainersConfig::Container::BindMount>
  getBindMountsForContainer(QString const& container_id);

  Q_INVOKABLE QString
  getContainerType(QString const& container_id);

  Q_INVOKABLE QString
  getContainerDistro(QString const& container_id);

  Q_INVOKABLE QString
  getContainerMultiarchSupport(QString const& container_id);

  Q_INVOKABLE QString
  getContainerName(QString const& container_id);

  Q_INVOKABLE QString
  getContainerStatus(QString const& container_id);

  Q_INVOKABLE bool
  getFreezeOnStop(QString const& container_id);

  Q_INVOKABLE QString
  getHostArchitecture();

  void
  reloadConfigs();

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

  void
  configChanged();

private:
  /**
   * Generates a bis (suffix) that can be used to distinguish between otherwise
   * identical container ids and names.
   */
  int
  generate_bis(QString const& distro_series);

  void
  clear_config();

  void
  load_config();

  QString
  getHostDistroCodename();

  QString
  getHostDistroDescription();

private:
  LibertineConfig const*            config_;
  QString                           default_container_id_;
  std::unique_ptr<ContainersConfig> containers_config_;
};
