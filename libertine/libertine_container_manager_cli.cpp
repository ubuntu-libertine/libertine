/**
 * @file libertine_container_manager_cli.cpp
 * @brief The CLI manager Libertine Containers
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

#include "libertine/libertine_lxc_manager_wrapper.h"
#include "libertine/ContainerConfigList.h"
#include "libertine/ContainerManager.h"
#include "libertine/LibertineConfig.h"
#include "libertine/config.h"

#include <iomanip>
#include <iostream>
#include <unistd.h>
#include <QCoreApplication>
#include <QtCore/QCommandLineParser>

using namespace std;

int main (int argc, char *argv[])
{
  LibertineConfig config;
  ContainerConfigList* containers;
  QCommandLineParser commandlineParser;

  QCoreApplication app(argc, argv);
  app.setApplicationName(LIBERTINE_APPLICATION_NAME);

  containers = new ContainerConfigList(&config);

  commandlineParser.setApplicationDescription("Command-line tool to manage sandboxes for running legacy DEB-packaged X11-based applications");
  commandlineParser.addHelpOption();

  commandlineParser.addPositionalArgument("command", "[create | destroy | install-package | update | list]");

  commandlineParser.parse(QCoreApplication::arguments());

  const QStringList args = commandlineParser.positionalArguments();
  const QString command = args.isEmpty() ? QString() : args.first();

  if (command == "create")
  {
    commandlineParser.clearPositionalArguments();
    commandlineParser.addPositionalArgument("create", "Create a new Libertine container.");
    commandlineParser.process(app);

    QVariantMap image;
    image.insert("id", "wily");
    image.insert("name", "Ubuntu 'Wily Werewolf'");
    QString container_id = containers->addNewContainer(image);

    ContainerManagerWorker *worker = new ContainerManagerWorker(ContainerManagerWorker::ContainerAction::Create, container_id);
    QObject::connect(worker, SIGNAL(finished()), &app, SLOT(quit()));
    worker->start();
  }
  else if (command == "destroy")
  {
    commandlineParser.clearPositionalArguments();
    commandlineParser.addPositionalArgument("destroy", QCoreApplication::translate("main", "Destroy an existing Libertine container."));
    commandlineParser.addOption({{"n", "name"}, QCoreApplication::translate("main", "Name of container"), "container_name"});

    commandlineParser.process(app);

    if (commandlineParser.isSet("name"))
    {
      const QString container_id = commandlineParser.value("name");

      if (containers->deleteContainer(container_id))
      {
        ContainerManagerWorker *worker = new ContainerManagerWorker(ContainerManagerWorker::ContainerAction::Destroy, container_id);
        QObject::connect(worker, SIGNAL(finished()), &app, SLOT(quit()));
        worker->start();
      }
      else
      {
        cout << QCoreApplication::translate("main", "The container name specified does not exist.").toStdString().c_str() << endl;
        return -1;
      }
    }
    else
    {
      cout << QCoreApplication::translate("main", "You must specify a container name when using the destroy command!").toStdString().c_str() << endl;
      commandlineParser.showHelp(-1);
    }
  }
  else if (command == "install-package")
  {
    commandlineParser.clearPositionalArguments();
    commandlineParser.addPositionalArgument("install-package", QCoreApplication::translate("main", "Install a package in an existing Libertine container."));

    commandlineParser.addOption({{"n", "name"}, QCoreApplication::translate("main", "Name of container"), "container_name"});
    commandlineParser.addOption({{"p", "package"}, QCoreApplication::translate("main", "Name of package to install"), "package_name"});

    commandlineParser.process(app);

    if (commandlineParser.isSet("name") && commandlineParser.isSet("package"))
    {
      const QString package_name = commandlineParser.value("install-package");
      const QString container_id = commandlineParser.value("name");

      ContainerManagerWorker *worker = new ContainerManagerWorker(ContainerManagerWorker::ContainerAction::Install, container_id, package_name);
      QObject::connect(worker, SIGNAL(finished()), &app, SLOT(quit()));
      worker->start();
    }
    else
    {
      cout << QCoreApplication::translate("main", "You must specify a container name & package name when using the install-package command!").toStdString().c_str() << endl;
      commandlineParser.showHelp(-1);
    }
  }
  else if (command == "update")
  {
    commandlineParser.clearPositionalArguments();
    commandlineParser.addPositionalArgument("update", QCoreApplication::translate("main", "Update packages in an existing Libertine container."));

    commandlineParser.addOption({{"n", "name"}, QCoreApplication::translate("main", "Name of container"), "container_name"});

    commandlineParser.process(app);

    if (commandlineParser.isSet("name"))
    {
      const QString container_id = commandlineParser.value("name");

      ContainerManagerWorker *worker = new ContainerManagerWorker(ContainerManagerWorker::ContainerAction::Update, container_id);
      QObject::connect(worker, SIGNAL(finished()), &app, SLOT(quit()));
      worker->start();
    }
    else
    {
      cout << QCoreApplication::translate("main", "You must specify a container name when using the update command!").toStdString().c_str() << endl;
      commandlineParser.showHelp(-1);
    }
  }
  else if (command == "list")
  {
    commandlineParser.clearPositionalArguments();
    commandlineParser.addPositionalArgument("list", "List all existing Libertine containers.");
    commandlineParser.process(app);

    int count = containers->size();
    QVariant name, id;

    cout << setw(10) << left << "id" << setw(30) << left << "Container Name" << endl;
    for (int i = 0; i < count; ++i)
    {
      name = containers->data(containers->index(i, 0), (int)ContainerConfigList::DataRole::ContainerName);
      id = containers->data(containers->index(i, 0), (int)ContainerConfigList::DataRole::ContainerId);
      cout << setw(10) << left << id.toString().toStdString() << setw(30) << left << name.toString().toStdString() << endl;
    }

    return 0;
  }
  else
  {
    cout << QCoreApplication::translate("main", "Invalid command specified!").toStdString().c_str() << endl;
    commandlineParser.showHelp(-1);
  }

  return app.exec();
}
