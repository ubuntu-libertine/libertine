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
{
  CreateContainerManager();
}


ContainerManagerWorker::
ContainerManagerWorker(ContainerAction container_action,
                       QString const& container_id,
                       QString const& container_type,
                       QString const& data)
: container_action_(container_action)
, container_id_(container_id)
, container_type_(container_type)
, data_(data)
{
  CreateContainerManager();
}


ContainerManagerWorker::
~ContainerManagerWorker()
{
  delete manager_;
}


void ContainerManagerWorker::
CreateContainerManager()
{
  manager_ = new LibertineManagerWrapper(container_id_.toStdString().c_str(), container_type_.toStdString().c_str());
}


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
  manager_->CreateLibertineContainer(password.toStdString().c_str());

  emit finished();
  quit();
}


void ContainerManagerWorker::
destroyContainer()
{
  manager_->DestroyLibertineContainer();

  emit finishedDestroy(container_id_);
  emit finished();
  quit();
}


void ContainerManagerWorker::
installPackage(QString const& package_name)
{
  char error_msg[1024];
  char *buff_ptr = error_msg;
  bool result;

  result = manager_->InstallPackageInContainer(package_name.toStdString().c_str(), &buff_ptr);

  emit finishedInstall(result, QString(error_msg));
  emit finished();
  quit();
}


void ContainerManagerWorker::
removePackage(QString const& package_name)
{
  char error_msg[1024];
  char *buff_ptr = error_msg;
  bool result;

  result = manager_->RemovePackageInContainer(package_name.toStdString().c_str(), &buff_ptr);

  emit finishedRemove(result, QString(error_msg));
  emit finished();
  quit();
}


void ContainerManagerWorker::
updateContainer()
{
  manager_->UpdateLibertineContainer();

  emit finished();
  quit();
}
