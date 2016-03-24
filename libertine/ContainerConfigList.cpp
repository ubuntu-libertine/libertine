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
#include "libertine/ContainerManager.h"
#include "libertine/ContainerConfigList.h"
#include "libertine/LibertineConfig.h"

#include <algorithm>
#include "libertine/ContainerConfig.h"
#include <QtCore/QDebug>
#include <QtCore/QFile>
#include <QtCore/QJsonArray>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonObject>
#include <QtCore/QJsonParseError>
#include <QtCore/QJsonValue>
#include <QtCore/QProcess>
#include <QtCore/QRegExp>
#include <QtCore/QSettings>
#include <QtCore/QString>
#include <QtCore/QSysInfo>

#include <sys/file.h>


const QString ContainerConfigList::Json_container_list = "containerList";
const QString ContainerConfigList::Json_default_container = "defaultContainer";


ContainerConfigList::
ContainerConfigList(QObject* parent)
: QAbstractListModel(parent)
{ }


ContainerConfigList::
ContainerConfigList(QJsonObject const& json_object,
                    QObject*           parent)
: QAbstractListModel(parent)
{
  if (!json_object.empty())
  {
    default_container_id_ = json_object[Json_default_container].toString();

    QJsonArray container_list = json_object[Json_container_list].toArray();
    for (auto const& config: container_list)
    {
      QJsonObject containerConfig = config.toObject();
      configs_.append(new ContainerConfig(containerConfig, this));
    }
  }
}


ContainerConfigList::
ContainerConfigList(LibertineConfig const* config,
                    QObject*               parent)
: QAbstractListModel(parent)
, config_(config)
{
  load_config();
}


ContainerConfigList::
~ContainerConfigList()
{ }


QString ContainerConfigList::
addNewContainer(QString const& type)
{
  QString distro_series = getHostDistroCodename();
  QString container_id = distro_series;
  QString name = getHostDistroDescription();

  int bis = generate_bis(container_id);
  if (bis > 0)
  {
    container_id = QString("%1-%2").arg(container_id).arg(bis);
    name = QString("%1 (%2)").arg(name).arg(bis);
  }

  configs_.append(new ContainerConfig(container_id, name, type, distro_series, this));
  if (this->size() == 1)
    default_container_id_ = container_id;

  beginResetModel();
  endResetModel();

  return container_id;
}


void ContainerConfigList::
deleteContainer()
{
  beginResetModel();
  endResetModel();  
}


QList<ContainerApps*> * ContainerConfigList::
getAppsForContainer(QString const& container_id)
{
  for (auto const& config: configs_)
  {
    if (config->container_id() == container_id)
    {
      return &(config->container_apps());
    }
  }
  return nullptr;
}


bool ContainerConfigList::
isAppInstalled(QString const& container_id, QString const& package_name)
{
  for (auto const& config: configs_)
  {
    if (config->container_id() == container_id)
    {
      for (auto const& app: config->container_apps())
      {
        if (app->package_name() == package_name)
        {
          return true;
        }
      }
    }
  }

  return false;
}


QString ContainerConfigList::
getAppStatus(QString const& container_id, QString const& package_name)
{
  for (auto const& config: configs_)
  {
    if (config->container_id() == container_id)
    {
      for (auto const& app: config->container_apps())
      {
        if (app->package_name() == package_name)
        {
          return app->app_status();
        }
      }
    }
  }

  return nullptr;
}


QString ContainerConfigList::
getAppVersion(QString const& app_info)
{
  if (app_info.startsWith("N:") || app_info.isEmpty())
  {
    return QString("Cannot determine package version.");
  }
  else
  {
    QStringList info = app_info.split('\n');

    return info.at(1).section(": ", 1, 1);
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
  
QList<ContainerArchives*> * ContainerConfigList::
getArchivesForContainer(QString const& container_id)
{
  for (auto const& config: configs_)
  {
    if (config->container_id() == container_id)
    {
      return &(config->container_archives());
    }
  }
  return nullptr;
}


QString ContainerConfigList::
getContainerType(QString const& container_id)
{
  QString default_type("lxc");

  for (auto const& config: configs_)
  {
    if (config->container_id() == container_id)
    {
      return config->container_type();
    }
  }
  return default_type;
}


QString ContainerConfigList::
getContainerDistro(QString const& container_id)
{
  for (auto const& config: configs_)
  {
    if (config->container_id() == container_id)
    {
      return config->distro_series();
    }
  }
  return nullptr;
}


QString ContainerConfigList::
getContainerName(QString const& container_id)
{
  for (auto const& config: configs_)
  {
    if (config->container_id() == container_id)
    {
      return config->name();
    }
  }
  return nullptr;
}


QString ContainerConfigList::
getContainerMultiarchSupport(QString const& container_id)
{
  for (auto const& config: configs_)
  {
    if (config->container_id() == container_id)
    {
      return config->multiarch_support();
    }
  }
  return nullptr;
}


QString ContainerConfigList::
getContainerStatus(QString const& container_id)
{
  for (auto const& config: configs_)
  {
    if (config->container_id() == container_id)
    {
      return config->install_status();
    }
  }
  return nullptr;
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
  QJsonObject json_object;
  json_object[Json_default_container] = default_container_id_;

  QJsonArray contents;
  for (auto const& config: configs_)
  {
    contents.append(config->toJson());
  }
  json_object[Json_container_list] = contents;

  return json_object;
}


QString const& ContainerConfigList::
default_container_id() const
{ return default_container_id_; }


void ContainerConfigList::
default_container_id(QString const& container_id)
{ default_container_id_ = container_id; }


bool ContainerConfigList::
empty() const noexcept
{ return configs_.empty(); }


ContainerConfigList::size_type ContainerConfigList::
size() const noexcept
{ return configs_.count(); }


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

  if (index.isValid() && index.row() <= configs_.count())
  {
    switch (static_cast<DataRole>(role))
    {
      case DataRole::ContainerId:
        result = configs_[index.row()]->container_id();
        break;
      case DataRole::ContainerName:
        result = configs_[index.row()]->name();
        break;
      case DataRole::ContainerType:
        result = configs_[index.row()]->container_type();
        break;
      case DataRole::DistroSeries:
        result = configs_[index.row()]->distro_series();
        break;
      case DataRole::InstallStatus:
        result = configs_[index.row()]->install_status();
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
  for (auto const& config: configs_)
  {
    int found = re.indexIn(config->container_id());
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
  for (auto const& config: configs_)
  {
    qDeleteAll(config->container_apps());
    config->container_apps().clear();
  }

  qDeleteAll(configs_);
  configs_.clear();
}


void ContainerConfigList::
load_config()
{
  QFile config_file(config_->containers_config_file_name());

  if (config_file.exists())
  {
    if (!config_file.open(QIODevice::ReadOnly))
    {
      qWarning() << "could not open containers config file " << config_file.fileName();
    }
    else if (config_file.size() != 0)
    {
      QJsonParseError parse_error;

      flock(config_file.handle(), LOCK_EX);
      QJsonDocument json = QJsonDocument::fromJson(config_file.readAll(), &parse_error);
      flock(config_file.handle(), LOCK_UN);

      if (parse_error.error)
      {
        qWarning() << "error parsing containers config file: " << parse_error.errorString();
      }
      if (!json.object().empty())
      {
        default_container_id_ = json.object()[Json_default_container].toString();

        if (!configs_.empty())
        {
          clear_config();
        }

        QJsonArray container_list = json.object()[Json_container_list].toArray();
        for (auto const& config: container_list)
        {
          QJsonObject containerConfig = config.toObject();
          configs_.append(new ContainerConfig(containerConfig, this));
        }
      }
    }
  }
}
