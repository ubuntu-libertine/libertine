/**
 * @file ContainerConfig.h
 * @brief Libertine Manager containers configuration module
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
#ifndef CONTAINER_CONTAINERCONFIG_H
#define CONTAINER_CONTAINERCONFIG_H

#include "libertine/libertine_lxc_manager_wrapper.h"

#include <QtCore/QJsonObject>
#include <QtCore/QObject>
#include <QtCore/QString>


class ContainerApps
: public QObject
{
  Q_OBJECT

public:
  enum class AppStatus
  { New, Installing, Installed, Failed };

public:
  ContainerApps(QString const& package_name,
                AppStatus app_status,
                QObject* parent = nullptr);
  ~ContainerApps();

  QString const&
  package_name() const;

  AppStatus
  app_status() const;

private:
  QString   package_name_;
  AppStatus app_status_;
};


/**
 * The runtime configuration of the Libertine tools.
 */
class ContainerConfig
: public QObject
{
  Q_OBJECT
  Q_ENUMS(InstallStatus)
  Q_PROPERTY(QString containerId READ container_id)
  Q_PROPERTY(QString name READ name WRITE name NOTIFY nameChanged)
  Q_PROPERTY(QString imageId READ image_id)
  Q_PROPERTY(InstallStatus installStatus READ install_status WRITE install_status NOTIFY installStatusChanged)

public:
  /** The container's current install state. */
  enum class InstallStatus
  { New, Downloading, Configuring, Ready };

public:
  ContainerConfig(QObject* parent = nullptr);
  ContainerConfig(QString const& container_id,
                  QString const& container_name,
                  QString const& image_id,
                  QObject*       parent = nullptr);
  ContainerConfig(QJsonObject const& json_object,
                  QObject*           parent = nullptr);
  ~ContainerConfig();

  QString const&
  container_id() const;

  QString const&
  name() const;

  void
  name(QString const& name);

  QString const&
  image_id() const;

  InstallStatus
  install_status() const;

  void
  install_status(InstallStatus install_status);

  QList<ContainerApps*> &
  container_apps();

  QJsonObject
  toJson() const;

signals:
  void nameChanged();
  void installStatusChanged();

private:
  QString               container_id_;
  QString               container_name_;
  QString               image_id_;
  InstallStatus         install_status_;
  QList<ContainerApps*> container_apps_;
};

#endif /* CONTAINER_CONTAINERCONFIG_H */
