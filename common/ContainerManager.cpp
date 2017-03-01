/**
 * @file ContainerManager.cpp
 * @brief Threaded Libertine container manager
 */
/*
 * Copyright 2015-2017 Canonical Ltd
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
#include "common/ContainerManager.h"

#include <QTemporaryFile>


namespace
{
static const QString FAILED_TO_START = QObject::tr("%1 failed to start");
static const QString PACKAGE_INSTALLATION_FAILED = QObject::tr("Installation of package %1 failed");
static const QString PACKAGE_REMOVAL_FAILED = QObject::tr("Removal of package %1 failed");
static const QString PACKAGE_SEARCH_FAILED = QObject::tr("Searching for query %1 failed");
static const QString CONTAINER_UPDATE_FAILED = QObject::tr("Updating container %1 failed");
static const QString CONTAINER_CREATE_FAILED = QObject::tr("Creating container %1 failed");
static const QString CONTAINER_DESTROY_FAILED = QObject::tr("Destroying container %1 failed");
static const QString RUN_COMMAND_FAILED = QObject::tr("Running command %1 failed");
static const QString CONTAINER_CONFIGURE_FAILED = QObject::tr("Attempt to configure container %1 failed");
static const QString SET_DEFAULT_CONTAINER_FAILED = QObject::tr("Attempt to set container as default failed");
static const QString GENERAL_ERROR = QObject::tr("An error occurred");
constexpr auto libertine_container_manager_tool = "libertine-container-manager";


static const QString readAllStdOutOrStdErr(QProcess& proc, const QString& default_output = "")
{
  QByteArray out = proc.readAllStandardOutput(),
             err = proc.readAllStandardError();
  return !out.isEmpty() ? out
                        : !err.isEmpty() ? err : default_output;
}


static void pidKiller(const QString& pid, bool shouldKill = true)
{
  QProcess list_child_pids;
  list_child_pids.start("pgrep", QStringList{"-P", pid});
  list_child_pids.waitForFinished();
  auto pids = QString::fromUtf8(list_child_pids.readAllStandardOutput()).split('\n', QString::SkipEmptyParts);
  for (const auto& child: pids)
  {
    pidKiller(child);
  }
  if (shouldKill)
  {
    QProcess::execute("kill " + pid);
  }
}
}


ContainerManagerWorker::
ContainerManagerWorker()
{
  connect(&process_, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished), this, &QObject::deleteLater);
  connect(&process_,
#if QT_VERSION >= QT_VERSION_CHECK(5, 6, 0)
          &QProcess::errorOccurred,
#else
          static_cast<void(QProcess::*)(QProcess::ProcessError)>(&QProcess::error),
#endif
          [=](QProcess::ProcessError) {
            emit error(GENERAL_ERROR, process_.errorString());
  });
}


ContainerManagerWorker::
~ContainerManagerWorker()
{
  if (process_.state() == QProcess::Running)
  {
    pidKiller(QString::number(process_.pid()), false);
    process_.close();
  }
}


void ContainerManagerWorker::
createContainer(const QString& id, const QString& name, const QString& distro, bool multiarch, const QString& password)
{
  connect(&process_, &QProcess::readyRead, [=](){
    auto output = process_.readAllStandardOutput();
    if (!output.isEmpty())
    {
      emit updateOperationDetails(id, output);
    }
  });
  connect(&process_, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
          [=](int exitCode, QProcess::ExitStatus){
    if (exitCode != 0)
    {
      emit error(CONTAINER_CREATE_FAILED.arg(id), process_.readAllStandardError());
    }
    emit operationFinished(id);
  });
  connect(&process_, &QProcess::started, [=]() {
    process_.write(password.toUtf8());
    process_.closeWriteChannel();
  });

  QStringList args{"create", "-i", id, "-d", distro, "-n", name};
  if (multiarch)
  {
    args << "-m";
  }
  process_.start(libertine_container_manager_tool, args);
}


void ContainerManagerWorker::
destroyContainer(const QString& id)
{
  connect(&process_, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
          [=](int exitCode, QProcess::ExitStatus){
    if (exitCode != 0)
    {
      emit error(CONTAINER_DESTROY_FAILED.arg(id), process_.readAllStandardError());
    }
    emit finishedDestroy(id);
  });

  process_.start(libertine_container_manager_tool, QStringList{"destroy", "-i", id});
}


void ContainerManagerWorker::
containerOperationInteraction(const QString& input)
{
  if (process_.state() == QProcess::Running)
  {
    process_.write(input.toUtf8() + "\n");
  }
}


void ContainerManagerWorker::
installPackage(const QString& container_id, const QString& package_name)
{
  connect(&process_, &QProcess::readyRead, [=](){
    auto output = process_.readAllStandardOutput();
    if (!output.isEmpty())
    {
      emit updateOperationDetails(container_id, output);
      process_output_ += output;
    }
  });
  connect(&process_, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
          [=](int exitCode, QProcess::ExitStatus){
    if (exitCode != 0)
    {
      auto stderr = process_.readAllStandardError();
      emit error(PACKAGE_INSTALLATION_FAILED.arg(package_name), stderr.isEmpty() ? process_output_ : stderr);
    }
     emit operationFinished(container_id);
  });

  process_.start(libertine_container_manager_tool, QStringList{"install-package", "-i", container_id, "-p", package_name, "--no-dialog"});
}


void ContainerManagerWorker::
removePackage(const QString& container_id, const QString& package_name)
{
  connect(&process_, &QProcess::readyRead, [=](){
    auto output = process_.readAllStandardOutput();
    if (!output.isEmpty())
    {
      emit updateOperationDetails(container_id, output);
      process_output_ += output;
    }
  });
  connect(&process_, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
          [=](int exitCode, QProcess::ExitStatus){
    if (exitCode != 0)
    {
      emit error(PACKAGE_INSTALLATION_FAILED.arg(package_name), readAllStdOutOrStdErr(process_, process_output_));
    }
    emit operationFinished(container_id);
  });

  process_.start(libertine_container_manager_tool, QStringList{"remove-package", "-i", container_id, "-p", package_name, "--no-dialog"});
}


void ContainerManagerWorker::
searchPackageCache(const QString& container_id, const QString& search_string)
{
  connect(&process_, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
          [=](int exitCode, QProcess::ExitStatus){
    QList<QString> packageList;
    if (exitCode != 0)
    {
      QString err(process_.readAllStandardError());
      if (!err.isEmpty())
      {
        emit error(PACKAGE_SEARCH_FAILED.arg(search_string), err);
      }
      // if there is no error message, there probably were no packages found
      // continue to return an empty list
    }
    else
    {
      auto search_output = process_.readAllStandardOutput();
      QList<QByteArray> packages = search_output.split('\n');

      for (const auto& package: packages)
      {
        packageList.append(QString(package));
      }
    }

    emit finishedSearch(packageList);
  });

  process_.start(libertine_container_manager_tool, QStringList{"search-cache", "-i", container_id, "-s", search_string});
}


void ContainerManagerWorker::
updateContainer(const QString& container_id, const QString& container_name)
{
  connect(&process_, &QProcess::readyRead, [=](){
    auto output = process_.readAllStandardOutput();
    if (!output.isEmpty())
    {
      emit updateOperationDetails(container_id, output);
    }
  });
  connect(&process_, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
          [=](int exitCode, QProcess::ExitStatus){
    if (exitCode != 0)
    {
      emit error(CONTAINER_UPDATE_FAILED.arg(container_name), readAllStdOutOrStdErr(process_));
    }
    emit operationFinished(container_id);
  });

  process_.start(libertine_container_manager_tool, QStringList{"update", "-i", container_id});
}


void ContainerManagerWorker::
runCommand(const QString& container_id, const QString& container_name, const QString& command_line)
{
  connect(&process_, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
          [=](int exitCode, QProcess::ExitStatus){
    if (exitCode != 0)
    {
      emit error(RUN_COMMAND_FAILED.arg(container_name), readAllStdOutOrStdErr(process_));
    }
    else
    {
      emit finishedCommand(process_.readAllStandardOutput());
    }
  });

  process_.start(libertine_container_manager_tool, QStringList{"exec", "-i", container_id, "-c", command_line});
}


void ContainerManagerWorker::
configureContainer(const QString& container_id, const QString& container_name, const QStringList& configure_command)
{
  connect(&process_, &QProcess::readyRead, [=](){
    auto output = process_.readAllStandardOutput();
    if (!output.isEmpty())
    {
      emit updateOperationDetails(container_id, output);
      process_output_ += output;
    }
  });
  connect(&process_, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
          [=](int exitCode, QProcess::ExitStatus){
    if (exitCode != 0)
    {
      emit error(CONTAINER_CONFIGURE_FAILED.arg(container_name), readAllStdOutOrStdErr(process_, process_output_));
    }
    else
    {
      emit finishedConfigure();
    }
    emit operationFinished(container_id);
  });

  QStringList args{"configure", "-i", container_id};
  args << configure_command.at(0) << configure_command.mid(1);
  process_.start(libertine_container_manager_tool, args);
}


void ContainerManagerWorker::
addArchive(const QString& container_id, const QString& container_name, const QString& archive, const QByteArray& signing_key)
{
  QStringList command{"--archive", "add", "--archive-name", archive};
  if (!signing_key.isEmpty())
  {
    QTemporaryFile keyfile;
    if (!keyfile.open())
    {
      emit error(CONTAINER_CONFIGURE_FAILED.arg(container_name), keyfile.errorString());
      return;
    }

    keyfile.setAutoRemove(false);
    keyfile.write(signing_key);

    command << "--public-key-file" << keyfile.fileName();
  }

  configureContainer(container_id, container_name, command);
}


void ContainerManagerWorker::
fixIntegrity()
{
  process_.start(libertine_container_manager_tool, QStringList{"fix-integrity"});
}


void ContainerManagerWorker::
setDefaultContainer(const QString& container_id, bool should_clear)
{
  connect(&process_, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
          [=](int exitCode, QProcess::ExitStatus){
    if (exitCode != 0)
    {
      emit error(SET_DEFAULT_CONTAINER_FAILED, readAllStdOutOrStdErr(process_));
    }
  });

  if (should_clear)
  {
    process_.start(libertine_container_manager_tool, QStringList{"set-default", "-c"});
  }
  else
  {
    process_.start(libertine_container_manager_tool, QStringList{"set-default", "-i", container_id});
  }
}
