/**
 * @file ContainerManager.cpp
 * @brief Threaded Libertine container manager
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
data() const
{ return data_; }


void ContainerManagerWorker::
data(QString const& data)
{
  data_ = data;
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

    case ContainerAction::Update:
      updateContainer();
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

  args << "create" << "-i" << container_id_ << "-t" << container_type_ << "-d" << "wily";

  libertine_cli_tool.start(exec_line, args);

  if (!libertine_cli_tool.waitForStarted())
      quit();

  libertine_cli_tool.write(password.toStdString().c_str()); 
  libertine_cli_tool.closeWriteChannel();

  libertine_cli_tool.waitForFinished();

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

  libertine_cli_tool.waitForFinished();

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

  libertine_cli_tool.waitForFinished();

  if (libertine_cli_tool.exitCode() != 0)
  {
    error_msg = libertine_cli_tool.readAllStandardError();
    result = false;
  }

  emit finishedInstall(result, QString(error_msg));
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

  libertine_cli_tool.waitForFinished();

  if (libertine_cli_tool.exitCode() != 0)
  {
    error_msg = libertine_cli_tool.readAllStandardError();
    result = false;
  }

  emit finishedRemove(result, QString(error_msg));
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

  libertine_cli_tool.waitForFinished();

  emit finished();
  quit();
}
