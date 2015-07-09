/**
 * @file ContainerConfigList.cpp
 * @brief Libertine Manager list of containers configurations
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
#include <QtCore/QRegExp>
#include <QtCore/QString>


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
  QFile config_file(config_->containers_config_file_name());

  if (config_file.exists())
  {
    if (!config_file.open(QIODevice::ReadOnly))
    {
      qWarning() << "could not open containers config file " << config_file.fileName();
    }
    else
    {
      QJsonParseError parse_error;
      QJsonDocument json = QJsonDocument::fromJson(config_file.readAll(), &parse_error);
      if (parse_error.error)
      {
        qWarning() << "error parsing containers config file: " << parse_error.errorString();
      }
      if (!json.object().empty())
      {
        default_container_id_ = json.object()[Json_default_container].toString();

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


ContainerConfigList::
~ContainerConfigList()
{ }


QString ContainerConfigList::
addNewContainer(QVariantMap const& image)
{
  QString image_id = image["id"].toString();
  QString id = image_id;
  QString name = image["name"].toString();
  int bis = generate_bis(image_id);
  if (bis > 0)
  {
    id = QString("%1-%2").arg(id).arg(bis);
    name = QString("%1 (%2)").arg(name).arg(bis);
  }

  beginInsertRows(QModelIndex(), rowCount(), rowCount());
  configs_.append(new ContainerConfig(id, name, image_id, this));
  if (this->size() == 1)
    default_container_id_ = id;

  save_container_config_list();
  endInsertRows();

  return id;
}


bool ContainerConfigList::
deleteContainer(QString const& container_id)
{
  bool found = false;

  for (int i = 0; i < rowCount(); ++i)
  {
    if (configs_[i]->container_id() == container_id)
    {
      found = true;

      beginRemoveRows(QModelIndex(), i, i);
      configs_.removeAt(i);

      if ((default_container_id_ == container_id) && !configs_.empty())
      {
        default_container_id_ = configs_.front()->container_id();
      }
      else
      {
        default_container_id_ = "";
      }

      save_container_config_list();
      endRemoveRows();
      break;
    }
  }
  return found;
}


bool ContainerConfigList::
addNewApp(QString const& container_id, QString const& package_name)
{
  for (int i = 0; i < rowCount(); ++i)
  {
    if (configs_[i]->container_id() == container_id)
    {
      for (auto const& app: configs_[i]->container_apps())
      {
        if (app->package_name() == package_name)
        {
          return false;
        }
      }
      configs_[i]->container_apps().append(new ContainerApps(package_name, ContainerApps::AppStatus::New, this));

      save_container_config_list();

      return true;
    }
  }
  return false;
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
  roles[static_cast<int>(DataRole::ImageId)]        = "imageId";
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
      case DataRole::ImageId:
        result = configs_[index.row()]->image_id();
        break;
      case DataRole::InstallStatus:
        result = static_cast<int>(configs_[index.row()]->install_status());
        break;
      case DataRole::Error:
        break;
    }
  }

  return result;
}


void ContainerConfigList::
save_container_config_list()
{
  QFile config_file(config_->containers_config_file_name());
  if (!config_file.open(QIODevice::WriteOnly))
  {
    qWarning() << "could not open containers config file " << config_file.fileName();
  }
  else
  {
    QJsonDocument jdoc(toJson());
    config_file.write(jdoc.toJson(QJsonDocument::Indented));
  }
}


int ContainerConfigList::
generate_bis(QString const& image_id)
{
  int bis = 0;
  int max = 0;
  QRegExp re = QRegExp("^(\\w*)(?:-(\\d+))?$", Qt::CaseInsensitive);
  for (auto const& config: configs_)
  {
    int found = re.indexIn(config->container_id());
    if (found >= 0 && re.cap(1) == image_id)
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

