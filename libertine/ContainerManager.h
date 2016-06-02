/**
 * @file ContainerManager.h
 * @brief Threaded Libertine container manager
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
#ifndef CONTAINER_CONTAINERMANAGER_H_
#define CONTAINER_CONTAINERMANAGER_H_

#include <QtCore/QObject>
#include <QtCore/QString>
#include <QtCore/QStringList>
#include <QtCore/QThread>
#include <QtCore/QProcess>

class ContainerManagerWorker
: public QObject
{
  Q_OBJECT

public:
  explicit ContainerManagerWorker();
  virtual ~ContainerManagerWorker();

  Q_INVOKABLE void createContainer(const QString& id, const QString& name, const QString& distro, bool multiarch, const QString& password);
  Q_INVOKABLE void destroyContainer(const QString& id);
  Q_INVOKABLE void installPackage(const QString& id, const QString& package_name);
  Q_INVOKABLE void removePackage(const QString& container_id, const QString& package_name);
  Q_INVOKABLE void searchPackageCache(const QString& container_id, const QString& search_string);
  Q_INVOKABLE void updateContainer(const QString& container_id, const QString& container_name);
  Q_INVOKABLE void runCommand(const QString& container_id, const QString& container_name, const QString& command_line);
  Q_INVOKABLE void configureContainer(const QString& container_id, const QString& container_name, const QStringList& configure_command);
  Q_INVOKABLE void fixIntegrity();

public slots:
  void packageOperationInteraction(const QString& input);

private:
  QProcess process_;
  QString process_output_;

signals:
  void containerActionChanged();
  void containerIdChanged();
  void containerTypeChanged();
  void containerDistroChanged();
  void containerNameChanged();
  void dataChanged();
  void dataListChanged();
  void finishedDestroy(QString const& container_id);
  void finishedInstall(QString const& package_name, bool result, QString const& error_msg);
  void finishedRemove(QString const& package_name, bool result, QString const& error_msg);
  void finishedSearch(QList<QString> packageList);
  void finishedCommand(QString const& command_output);
  void finishedConfigure();
  void updatePackageOperationDetails(const QString& container_id, const QString& package_name, const QString& details);
  void packageOperationFinished(const QString& container_id, const QString& package_name);

  void error(const QString& short_description, const QString& details);
};

#endif /* CONTAINER_CONTAINERMANAGER_H_ */
