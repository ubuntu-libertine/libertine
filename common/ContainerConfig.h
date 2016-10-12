/**
 * @file ContainerConfig.h
 * @brief Libertine Manager containers configuration module
 */
/*
 * Copyright 2015-2016 Canonical Ltd
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

#include <QtCore/QJsonObject>
#include <QtCore/QObject>
#include <QtCore/QString>


enum class CurrentStatus { New, Installing, Installed, Failed, Removing, Removed };


class ContainerApps
: public QObject
{
  Q_OBJECT

public:
  ContainerApps(QString const& package_name,
                CurrentStatus app_status,
                QObject* parent = nullptr);
  ~ContainerApps();

  QString const&
  package_name() const;

  QString const&
  app_status() const;

private:
  QString       package_name_;
  CurrentStatus app_status_;
};


class ContainerArchives
: public QObject
{
  Q_OBJECT

public:
  ContainerArchives(QString const& archive_name,
                    CurrentStatus archive_status,
                    QObject* parent = nullptr);
  ~ContainerArchives();

  QString const&
  archive_name() const;

  QString const&
  archive_status() const;

private:
  QString archive_name_;
  CurrentStatus archive_status_;
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
  Q_PROPERTY(QString distroSeries READ distro_series)

public:
  /** The container's current install state. */
  enum class InstallStatus
  { New, Installing, Ready, Updating, Removing, Removed, Failed };


public:
  ContainerConfig(QObject* parent = nullptr);
  ContainerConfig(QString const& container_id,
                  QString const& container_name,
                  QString const& container_type,
                  QString const& distro_series,
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
  container_type() const;

  QString const&
  distro_series() const;

  QString const&
  multiarch_support() const;

  QString const&
  install_status() const;

  void
  install_status(InstallStatus install_status);

  QList<ContainerApps*> &
  container_apps();

  QList<ContainerArchives*> &
  container_archives();

  QJsonObject
  toJson() const;

signals:
  void nameChanged();
  void installStatusChanged();

private:
  QString                   container_id_;
  QString                   container_name_;
  QString                   container_type_;
  QString                   distro_series_;
  QString                   multiarch_support_;
  InstallStatus             install_status_;
  QList<ContainerApps*>     container_apps_;
  QList<ContainerArchives*> container_archives_;
};

#endif /* CONTAINER_CONTAINERCONFIG_H */
