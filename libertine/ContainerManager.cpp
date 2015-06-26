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
                       QString const& package_name)
: container_action_(container_action)
, container_id_(container_id)
, package_name_(package_name)
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
package_name() const
{ return package_name_; }


void ContainerManagerWorker::
package_name(QString const& package_name)
{
  package_name_ = package_name;
}


void ContainerManagerWorker::
run()
{
  switch(container_action_)
  {
    case ContainerAction::Create:
      createContainer(container_id_);
      break;

    case ContainerAction::Destroy:
      destroyContainer(container_id_);
      break;

    case ContainerAction::Install:
      installPackage(container_id_, package_name_);
      break;

    case ContainerAction::Update:
      updateContainer(container_id_);
      break;

    default:
      break;
  }
}


void ContainerManagerWorker::
createContainer(QString const& container_id)
{
  LibertineManagerWrapper manager(container_id.toStdString().c_str());

  manager.CreateLibertineContainer("123456");

  emit finished();
}


void ContainerManagerWorker::
destroyContainer(QString const& container_id)
{
  LibertineManagerWrapper manager(container_id.toStdString().c_str());

  manager.DestroyLibertineContainer();

  emit finishedDestroy();
  emit finished();
}


void ContainerManagerWorker::
installPackage(QString const& container_id, QString const& package_name)
{
  LibertineManagerWrapper manager(container_id.toStdString().c_str());

  emit finished();
}


void ContainerManagerWorker::
updateContainer(QString const& container_id)
{
  LibertineManagerWrapper manager(container_id.toStdString().c_str());

  emit finished();
}
