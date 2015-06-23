
#ifndef CONTAINER_CONTAINERMANAGER_H_
#define CONTAINER_CONTAINERMANAGER_H_

#include "libertine/libertine_lxc_manager_wrapper.h"

#include <QtCore/QObject>
#include <QtCore/QString>
#include <QtCore/QThread>

class ContainerManagerWorker
: public QObject
{
  Q_OBJECT

public:
  ContainerManagerWorker(QObject* parent = nullptr);
  ~ContainerManagerWorker();

public slots:
  void createContainer(QString const& container_id);
  void destroyContainer(QString const& container_id);
  void installPackage(QString const& container_id, QString const& package_name);
  void updateContainer(QString const& container_id);

signals:
  void finished();
};

class ContainerManagerController
: public QObject
{
  Q_OBJECT

public:
  ContainerManagerController(QObject* parent = nullptr);
  ~ContainerManagerController();

public:
  QThread workerThread;
  ContainerManagerWorker *worker;

public slots:
  void threadQuit();

signals:
  void doCreate(QString const& container_id = nullptr);
  void doDestroy(QString const& container_id = nullptr);
  void doInstall(QString const& container_id = nullptr,
                 QString const& package_name = nullptr);
  void doUpdate(QString const& container_id = nullptr);
};

#endif /* CONTAINER_CONTAINERMANAGER_H_ */
