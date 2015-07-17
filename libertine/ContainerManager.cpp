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
                       QString const& container_id)
: container_action_(container_action)
, container_id_(container_id)
{

}


ContainerManagerWorker::
ContainerManagerWorker(ContainerAction container_action,
                       QString const& container_id,
                       QString const& data)
: container_action_(container_action)
, container_id_(container_id)
, data_(data)
{

}


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
      createContainer(container_id_, data_);
      break;

    case ContainerAction::Destroy:
      destroyContainer(container_id_);
      break;

    case ContainerAction::Install:
      installPackage(container_id_, data_);
      break;

    case ContainerAction::Update:
      updateContainer(container_id_);
      break;

    default:
      break;
  }
}


void ContainerManagerWorker::
createContainer(QString const& container_id, QString const& password)
{
  LibertineManagerWrapper manager(container_id.toStdString().c_str());

  manager.CreateLibertineContainer(password.toStdString().c_str());

  emit finished();
  quit();
}


void ContainerManagerWorker::
destroyContainer(QString const& container_id)
{
  LibertineManagerWrapper manager(container_id.toStdString().c_str());

  manager.DestroyLibertineContainer();

  emit finishedDestroy(container_id);
  emit finished();
  quit();
}


void ContainerManagerWorker::
installPackage(QString const& container_id, QString const& package_name)
{
  char error_msg[1024];
  char *buff_ptr = error_msg;
  bool result;

  LibertineManagerWrapper manager(container_id.toStdString().c_str());

  result = manager.InstallPackageInContainer(package_name.toStdString().c_str(), &buff_ptr);

  emit finishedInstall(result, QString(error_msg));
  emit finished();
  quit();
}


void ContainerManagerWorker::
updateContainer(QString const& container_id)
{
  LibertineManagerWrapper manager(container_id.toStdString().c_str());

  manager.UpdateLibertineContainer();

  emit finished();
  quit();
}
