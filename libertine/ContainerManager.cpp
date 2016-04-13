/**
 * @file ContainerManager.cpp
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
#include "libertine/ContainerManager.h"

#include <QtCore/QProcess>


const QString ContainerManagerWorker::libertine_container_manager_tool = "libertine-container-manager";


ContainerManagerWorker::
ContainerManagerWorker()
{ }


ContainerManagerWorker::
ContainerManagerWorker(ContainerAction container_action,
                       QString const& container_id,
                       QString const& container_type)
: container_action_(container_action)
, container_id_(container_id)
, container_type_(container_type)
{ }


ContainerManagerWorker::
ContainerManagerWorker(ContainerAction container_action,
                       QString const& container_id,
                       QString const& container_type,
                       QString const& data)
: container_action_(container_action)
, container_id_(container_id)
, container_type_(container_type)
, data_(data)
{ }


ContainerManagerWorker::
ContainerManagerWorker(ContainerAction container_action,
                       QString const& container_id,
                       QString const& container_type,
                       QStringList data_list)
: container_action_(container_action)
, container_id_(container_id)
, container_type_(container_type)
, data_list_(data_list)
{ }


ContainerManagerWorker::
~ContainerManagerWorker()
{ }


ContainerManagerWorker::ContainerAction ContainerManagerWorker::
container_action() const
{ return container_action_; }


void ContainerManagerWorker::
container_action(ContainerAction container_action)
{
  container_action_ = container_action;
}


QString const& ContainerManagerWorker::
container_id() const
{ return container_id_; }


void ContainerManagerWorker::
container_id(QString const& container_id)
{
  container_id_ = container_id;
}


QString const& ContainerManagerWorker::
container_type() const
{ return container_type_; }


void ContainerManagerWorker::
container_type(QString const& container_type)
{
  container_type_ = container_type;
}


QString const& ContainerManagerWorker::
container_distro() const
{ return container_distro_; }


void ContainerManagerWorker::
container_distro(QString const& container_distro)
{
  if (container_distro != container_distro_)
  {
    container_distro_ = container_distro;
  }
}


QString const& ContainerManagerWorker::
container_name() const
{ return container_name_; }


void ContainerManagerWorker::
container_name(QString const& container_name)
{
  if (container_name != container_name_)
  {
    container_name_ = container_name;
  }
}


bool ContainerManagerWorker::
container_multiarch()
{ return container_multiarch_; }


void ContainerManagerWorker::
container_multiarch(bool container_multiarch)
{
  if (container_multiarch != container_multiarch_)
  {
    container_multiarch_ = container_multiarch;
  }
}


QString const& ContainerManagerWorker::
data() const
{ return data_; }


void ContainerManagerWorker::
data(QString const& data)
{
  data_ = data;
}


QStringList ContainerManagerWorker::
data_list()
{ return data_list_; }


void ContainerManagerWorker::
data_list(QStringList data_list)
{
  data_list_ = data_list;
}


void ContainerManagerWorker::
run()
{
  switch(container_action_)
  {
    case ContainerAction::Create:
      createContainer(data_);
      break;

    case ContainerAction::Destroy:
      destroyContainer();
      break;

    case ContainerAction::Install:
      installPackage(data_);
      break;

    case ContainerAction::Remove:
      removePackage(data_);
      break;

    case ContainerAction::Search:
      searchPackageCache(data_);
      break;

    case ContainerAction::Update:
      updateContainer();
      break;

    case ContainerAction::Exec:
      runCommand(data_);
      break;

    case ContainerAction::Configure:
      configureContainer(data_list_);
      break;

    default:
      break;
  }
}


void ContainerManagerWorker::
createContainer(QString const& password)
{
  QProcess libertine_cli_tool;
  QString exec_line = libertine_container_manager_tool;
  QStringList args;

  args << "create" << "-i" << container_id_ << "-d" << container_distro_ << "-n" << container_name_;

  if (container_multiarch_)
    args << "-m";

  libertine_cli_tool.start(exec_line, args);

  if (!libertine_cli_tool.waitForStarted())
    quit();

  libertine_cli_tool.write(password.toStdString().c_str()); 
  libertine_cli_tool.closeWriteChannel();

  libertine_cli_tool.waitForFinished(-1);

  emit finished();
  quit();
}


void ContainerManagerWorker::
destroyContainer()
{
  QProcess libertine_cli_tool;
  QString exec_line = libertine_container_manager_tool;
  QStringList args;

  args << "destroy" << "-i" << container_id_;
  libertine_cli_tool.start(exec_line, args);

  if (!libertine_cli_tool.waitForStarted())
    quit();

  libertine_cli_tool.waitForFinished(-1);

  emit finishedDestroy(container_id_);
  emit finished();
  quit();
}


void ContainerManagerWorker::
installPackage(QString const& package_name)
{
  QByteArray error_msg;
  bool result = true;

  QProcess libertine_cli_tool;
  QString exec_line = libertine_container_manager_tool;
  QStringList args;

  args << "install-package" << "-i" << container_id_ << "-p" << package_name;

  libertine_cli_tool.start(exec_line, args);

  if (!libertine_cli_tool.waitForStarted())
    quit();

  libertine_cli_tool.waitForFinished(-1);

  if (libertine_cli_tool.exitCode() != 0)
  {
    error_msg = libertine_cli_tool.readAllStandardError();
    result = false;
  }

  emit finishedInstall(package_name, result, QString(error_msg));
  emit finished();
  quit();
}


void ContainerManagerWorker::
removePackage(QString const& package_name)
{
  QByteArray error_msg;
  bool result = true;

  QProcess libertine_cli_tool;
  QString exec_line = libertine_container_manager_tool;
  QStringList args;

  args << "remove-package" << "-i" << container_id_ << "-p" << package_name;
  libertine_cli_tool.start(exec_line, args);

  if (!libertine_cli_tool.waitForStarted())
    quit();

  libertine_cli_tool.waitForFinished(-1);

  if (libertine_cli_tool.exitCode() != 0)
  {
    error_msg = libertine_cli_tool.readAllStandardError();
    result = false;
  }

  emit finishedRemove(package_name, result, QString(error_msg));
  emit finished();
  quit();
}


void ContainerManagerWorker::
searchPackageCache(QString const& search_string)
{
  QProcess libertine_cli_tool;
  QString exec_line = libertine_container_manager_tool;
  QStringList args;
  QByteArray search_output;
  QList<QString> packageList;
  bool result = true;

  args << "search-cache" << "-i" << container_id_ << "-s" << search_string;
  libertine_cli_tool.start(exec_line, args);

  if (!libertine_cli_tool.waitForStarted())
    quit();

  libertine_cli_tool.waitForFinished(-1);

  search_output = libertine_cli_tool.readAllStandardOutput();

  if (search_output.isEmpty())
  {
    result = false;
  }
  else
  {
    QList<QByteArray> packages = search_output.split('\n');

    foreach (const QByteArray &package, packages)
    {
      packageList.append(QString(package));
    }
  }

  emit finishedSearch(result, packageList);
  emit finished();
  quit();
}


void ContainerManagerWorker::
updateContainer()
{
  QProcess libertine_cli_tool;
  QString exec_line = libertine_container_manager_tool;
  QStringList args;

  args << "update" << "-i" << container_id_;

  libertine_cli_tool.start(exec_line, args);

  if (!libertine_cli_tool.waitForStarted())
    quit();

  libertine_cli_tool.waitForFinished(-1);

  emit finished();
  quit();
}


void ContainerManagerWorker::
runCommand(QString const& command_line)
{
  QProcess libertine_cli_tool;
  QString exec_line = libertine_container_manager_tool;
  QStringList args;
  QByteArray command_output;

  args << "exec" << "-i" << container_id_ << "-c" << command_line;

  libertine_cli_tool.start(exec_line, args);

  if (!libertine_cli_tool.waitForStarted())
    quit();

  libertine_cli_tool.waitForFinished(-1);

  command_output = libertine_cli_tool.readAllStandardOutput();

  emit finishedCommand(QString(command_output));
  quit();
}


void ContainerManagerWorker::
configureContainer(QStringList configure_command)
{
  QByteArray error_msg;
  bool result = true;

  QProcess libertine_cli_tool;
  QString exec_line = libertine_container_manager_tool;
  QStringList args;

  args << "configure" << "-i" << container_id_ << configure_command.at(0) << configure_command.mid(1);

    libertine_cli_tool.start(exec_line, args);

  if (!libertine_cli_tool.waitForStarted())
    quit();

  libertine_cli_tool.waitForFinished(-1);

  if (libertine_cli_tool.exitCode() != 0)
  {
    error_msg = libertine_cli_tool.readAllStandardOutput();
    result = false;
  }

  emit finishedConfigure(result, QString(error_msg));
  emit finished();
  quit();
}
