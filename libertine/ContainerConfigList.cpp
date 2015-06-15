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
#include "libertine/ContainerConfigList.h"

#include <algorithm>
#include "libertine/ContainerConfig.h"
#include <QtCore/QDebug>
#include <QtCore/QJsonArray>
#include <QtCore/QJsonObject>
#include <QtCore/QJsonValue>
#include <QtCore/QRegExp>
#include <QtCore/QString>


const QString ContainerConfigList::Json_object_name = "containerConfigs";


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
    QJsonArray containerConfigs = json_object[Json_object_name].toArray();
    for (auto const& config: containerConfigs)
    {
      QJsonObject containerConfig = config.toObject();
      configs_.append(new ContainerConfig(containerConfig, this));
    }
  }
}


ContainerConfigList::
~ContainerConfigList()
{ }


void ContainerConfigList::
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
  emit dataChanged();
  endInsertRows();
}


QJsonObject ContainerConfigList::
toJson() const
{
  QJsonArray contents;
  for (auto const& config: configs_)
  {
    contents.append(config->toJson());
  }

  QJsonObject json_object;
  json_object[Json_object_name] = contents;
  return json_object;
}


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

