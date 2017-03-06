/**
 * @file ContainerConfigList.cpp
 * @brief Libertine Manager list of containers configurations
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
#include "common/ContainerConfigList.h"

#include "common/LibertineConfig.h"
#include <algorithm>
#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QJsonArray>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonObject>
#include <QtCore/QJsonParseError>
#include <QtCore/QJsonValue>
#include <QtCore/QProcess>
#include <QtCore/QRegExp>
#include <QtCore/QSettings>
#include <QtCore/QStandardPaths>
#include <QtCore/QString>
#include <QtCore/QSysInfo>
#include <sys/file.h>


namespace
{
static constexpr auto POLICY_INSTALLED_VERSION_LINE = 1;
static constexpr auto POLICY_CANDIDATE_VERSION_LINE = 2;

static ContainersConfig::Container
find_container_by_id(QList<ContainersConfig::Container> const& containers, QString const& id)
{
  for (auto const& container: containers)
  {
    if (container.id == id)
    {
      return container;
    }
  }

  return ContainersConfig::Container();
}
}


const QString ContainerConfigList::Json_container_list = "containerList";
const QString ContainerConfigList::Json_default_container = "defaultContainer";


ContainerConfigList::
ContainerConfigList(QObject* parent)
: QAbstractListModel(parent)
, containers_config_(new ContainersConfig())
{ }


ContainerConfigList::
ContainerConfigList(LibertineConfig const* config,
                    QObject*               parent)
: QAbstractListModel(parent)
, config_(config)
, containers_config_(new ContainersConfig())
{
  load_config();
}


ContainerConfigList::
ContainerConfigList(QJsonObject const& json_object,
                    QObject*               parent)
: QAbstractListModel(parent)
, containers_config_(new ContainersConfig(json_object))
{
}


void ContainerConfigList::
reloadContainerList()
{
  beginResetModel();
  endResetModel();
}


void ContainerConfigList::
deleteContainer()
{ reloadContainerList(); }


QString ContainerConfigList::
addNewContainer(QString const& type, QString name)
{
  QString distro_series = getHostDistroCodename();
  QString container_id = distro_series;

  int bis = generate_bis(container_id);
  if (bis > 0)
  {
    container_id = QString("%1-%2").arg(container_id).arg(bis);
    if (name.isEmpty())
    {
        name = getHostDistroDescription();
        name = QString("%1 (%2)").arg(name).arg(bis);
    }
  }

  containers_config_->containers.append(ContainersConfig::Container(container_id, name, type, distro_series));
  if (this->size() == 1)
    default_container_id_ = container_id;

  return container_id;
}


QList<ContainersConfig::Container::InstalledApp> ContainerConfigList::
getAppsForContainer(QString const& container_id)
{
  return find_container_by_id(containers_config_->containers, container_id).installed_apps;
}


bool ContainerConfigList::
isAppInstalled(QString const& container_id, QString const& package_name)
{
  for (auto const& app: find_container_by_id(containers_config_->containers, container_id).installed_apps)
  {
    if (app.name == package_name)
    {
      return true;
    }
  }
  return false;
}


QString ContainerConfigList::
getAppStatus(QString const& container_id, QString const& package_name)
{
  for (auto const& app: find_container_by_id(containers_config_->containers, container_id).installed_apps)
  {
    if (app.name == package_name)
    {
      return app.status;
    }
  }
  return "";
}


QString ContainerConfigList::
getAppVersion(QString const& app_info, bool installed)
{
  if (app_info.startsWith("N:") || app_info.isEmpty())
  {
    return QString("Cannot determine package version.");
  }
  else
  {
    QStringList info = app_info.split('\n');
    return info.at(installed ? POLICY_INSTALLED_VERSION_LINE : POLICY_CANDIDATE_VERSION_LINE)
               .section(": ", 1, 1);
  }
}


bool ContainerConfigList::
isValidDebianPackage(QString const& package_string)
{
  return (package_string.endsWith(".deb") &&
          QFile::exists(package_string));
}


QString ContainerConfigList::
getDebianPackageName(QString const& package_path)
{
  QProcess cmd;
  QString exec_line("dpkg-deb");
  QStringList args;
  QByteArray package_name;

  args << "-f" << package_path << "Package";

  cmd.start(exec_line, args);

  if (!cmd.waitForStarted())
    return QString(package_name);

  cmd.waitForFinished(-1);

  package_name = cmd.readAllStandardOutput();

  return QString(package_name.trimmed());
}


QString ContainerConfigList::
getDownloadsLocation()
{
  return QStandardPaths::writableLocation(QStandardPaths::DownloadLocation);
}


QStringList ContainerConfigList::
getDebianPackageFiles()
{
  QStringList filters;
  QDir downloads(getDownloadsLocation());

  filters << "*.deb";

  return downloads.entryList(filters);
}


QList<ContainersConfig::Container::Archive> ContainerConfigList::
getArchivesForContainer(QString const& container_id)
{
  return find_container_by_id(containers_config_->containers, container_id).archives;
}


QList<ContainersConfig::Container::BindMount> ContainerConfigList::
getBindMountsForContainer(QString const& container_id)
{
  return find_container_by_id(containers_config_->containers, container_id).mounts;
}


QString ContainerConfigList::
getContainerType(QString const& container_id)
{
  return find_container_by_id(containers_config_->containers, container_id).type;
}


QString ContainerConfigList::
getContainerDistro(QString const& container_id)
{
  return find_container_by_id(containers_config_->containers, container_id).distro;
}


QString ContainerConfigList::
getContainerName(QString const& container_id)
{
  return find_container_by_id(containers_config_->containers, container_id).name;
}


QString ContainerConfigList::
getContainerMultiarchSupport(QString const& container_id)
{
  return find_container_by_id(containers_config_->containers, container_id).multiarch;
}


QString ContainerConfigList::
getContainerStatus(QString const& container_id)
{
  return find_container_by_id(containers_config_->containers, container_id).status;
}


bool ContainerConfigList::
getFreezeOnStop(QString const& container_id)
{
  return find_container_by_id(containers_config_->containers, container_id).freeze;
}


QString ContainerConfigList::
getHostArchitecture()
{
  return QSysInfo::currentCpuArchitecture();
}


QString ContainerConfigList::
getHostDistroCodename()
{
  QSettings distro_info("/etc/lsb-release", QSettings::NativeFormat);

  return distro_info.value("DISTRIB_CODENAME").toString();
}


QString ContainerConfigList::
getHostDistroDescription()
{
  QSettings distro_info("/etc/lsb-release", QSettings::NativeFormat);

  return distro_info.value("DISTRIB_DESCRIPTION").toString().section(' ', 0, 2);
}


void ContainerConfigList::
reloadConfigs()
{
  load_config();
  emit configChanged();
}


QJsonObject ContainerConfigList::
toJson() const
{
  return containers_config_->dump();
}


QString const& ContainerConfigList::
default_container_id() const
{ return containers_config_->default_container; }


void ContainerConfigList::
default_container_id(QString const& container_id)
{ containers_config_->default_container = container_id; }


bool ContainerConfigList::
empty() const noexcept
{ return containers_config_->containers.empty(); }


ContainerConfigList::size_type ContainerConfigList::
size() const noexcept
{ return containers_config_->containers.count(); }


int ContainerConfigList::
rowCount(QModelIndex const&) const
{
  return this->size();
}


QHash<int, QByteArray> ContainerConfigList::
roleNames() const
{
  QHash<int, QByteArray> roles;
  roles[static_cast<int>(DataRole::ContainerId)]    = "containerId";
  roles[static_cast<int>(DataRole::ContainerName)]  = "name";
  roles[static_cast<int>(DataRole::ContainerType)]  = "type";
  roles[static_cast<int>(DataRole::DistroSeries)]   = "distroSeries";
  roles[static_cast<int>(DataRole::InstallStatus)]  = "installStatus";
  return roles;
}


QVariant ContainerConfigList::
data(QModelIndex const& index, int role) const
{
  QVariant result;

  if (index.isValid() && index.row() <= containers_config_->containers.count())
  {
    switch (static_cast<DataRole>(role))
    {
      case DataRole::ContainerId:
        result = containers_config_->containers[index.row()].id;
        break;
      case DataRole::ContainerName:
        result = containers_config_->containers[index.row()].name;
        break;
      case DataRole::ContainerType:
        result = containers_config_->containers[index.row()].type;
        break;
      case DataRole::DistroSeries:
        result = containers_config_->containers[index.row()].distro;
        break;
      case DataRole::InstallStatus:
        result = containers_config_->containers[index.row()].status;
        break;
      case DataRole::Error:
        break;
    }
  }

  return result;
}


int ContainerConfigList::
generate_bis(QString const& id)
{
  int bis = 0;
  int max = 0;
  QRegExp re = QRegExp("^(\\w*)(?:-(\\d+))?$", Qt::CaseInsensitive);
  for (auto const& container: containers_config_->containers)
  {
    int found = re.indexIn(container.id);
    if (found >= 0 && re.cap(1) == id)
    {
      ++bis;
      bool ok;
      int val = re.cap(2).toInt(&ok);
      if (ok && val > 0)
        max = std::max(bis, val);
    }
  }
  if (bis > 0)
    bis = std::max(bis, max) + 1;
  return bis;
}


void ContainerConfigList::
clear_config()
{
  containers_config_.reset();
}


void ContainerConfigList::
load_config()
{
  QFile config_file(config_->containers_config_file_name());
  flock(config_file.handle(), LOCK_EX);

  if (config_file.exists())
  {
    if (!config_file.open(QIODevice::ReadOnly))
    {
      qWarning() << "could not open containers config file " << config_file.fileName();
    }
    else if (config_file.size() != 0)
    {
      QJsonParseError parse_error;
      QJsonDocument json = QJsonDocument::fromJson(config_file.readAll(), &parse_error);

      if (parse_error.error)
      {
        qWarning() << "error parsing containers config file: " << parse_error.errorString();
      }
      else
      {
        containers_config_.reset(new ContainersConfig(json.object()));
      }
    }
  }
  flock(config_file.handle(), LOCK_UN);
}
