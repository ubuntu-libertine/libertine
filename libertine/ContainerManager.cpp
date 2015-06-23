
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
