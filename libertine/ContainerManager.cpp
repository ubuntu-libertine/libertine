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
ContainerManagerWorker(QObject* parent)
: QObject(parent)
{

}

ContainerManagerWorker::
~ContainerManagerWorker()
{ }


void ContainerManagerWorker::
createContainer(QString const& container_id)
{
  LibertineManagerWrapper manager(container_id.toStdString().c_str());

  manager.CreateLibertineContainer("tesb5rotj6");

  emit finished();
}

void ContainerManagerWorker::
destroyContainer(QString const& container_id)
{
  LibertineManagerWrapper manager(container_id.toStdString().c_str());

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


ContainerManagerController::
ContainerManagerController(QObject* parent)
: QObject(parent)
{
  worker = new ContainerManagerWorker;

  worker->moveToThread(&workerThread);
  QObject::connect(&workerThread, &QThread::finished, worker, &QObject::deleteLater);
  QObject::connect(worker, &ContainerManagerWorker::finished, this, &ContainerManagerController::threadQuit);
  QObject::connect(this, &ContainerManagerController::doCreate, worker, &ContainerManagerWorker::createContainer);
  QObject::connect(this, &ContainerManagerController::doDestroy, worker, &ContainerManagerWorker::destroyContainer);
  QObject::connect(this, &ContainerManagerController::doInstall, worker, &ContainerManagerWorker::installPackage);
  QObject::connect(this, &ContainerManagerController::doUpdate, worker, &ContainerManagerWorker::updateContainer);
}

ContainerManagerController::
~ContainerManagerController()
{ }

void ContainerManagerController::
threadQuit()
{
  workerThread.quit();
}
