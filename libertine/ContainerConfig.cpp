/**
 * @file ContainerConfig.cpp
 * @brief Libertine Manager containers configuration module
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
#include "libertine/ContainerConfig.h"

#include <QtCore/QJsonObject>
#include <QtCore/QJsonValue>
#include <stdexcept>


namespace {
  /**
   * Extracts the container id from a JSON object.
   *
   * The container id must exist and be non-empty.
   */
  QString
  extract_container_id_from_json(QJsonObject const& json_object)
  {
    QJsonValue value = json_object["id"];
    if (value == QJsonValue::Undefined)
    {
        throw std::runtime_error("container id not found in JSON object");
    }

    QJsonValue::Type value_type = value.type();
    if (value_type != QJsonValue::String)
    {
        throw std::runtime_error("container id not valid type in JSON object");
    }

    QString id = value.toString();
    if (id.length() == 0)
    {
        throw std::runtime_error("container id empty in JSON object");
    }

    return id;
  }

  QString
  extract_container_name_from_json(QJsonObject const& json_object,
                                   QString const&     container_id)
  {
    QString name = container_id;
    QJsonValue value = json_object["name"];
    if (value != QJsonValue::Undefined)
    {
      QJsonValue::Type value_type = value.type();
      if (value_type == QJsonValue::String)
      {
        QString s = value.toString();
        if (s.length() > 0)
        {
          name = s;
        }
      }
    }
    
    return name;
  }

  QString
  extract_image_id_from_json(QJsonObject const& json_object,
                             QString const&     container_id)
  {
    QString image = container_id;
    QJsonValue value = json_object["image"];
    if (value != QJsonValue::Undefined)
    {
      QJsonValue::Type value_type = value.type();
      if (value_type == QJsonValue::String)
      {
        QString s = value.toString();
        if (s.length() > 0)
        {
          image = s;
        }
      }
    }

    return image;
  }

  const static struct { QString string; ContainerConfig::InstallStatus enumeration; } install_status_names[] =
  {
    { "new",          ContainerConfig::InstallStatus::New         },
    { "downloading",  ContainerConfig::InstallStatus::Downloading },
    { "configuring",  ContainerConfig::InstallStatus::Configuring },
    { "ready",        ContainerConfig::InstallStatus::Ready       },
    { QString(),      ContainerConfig::InstallStatus::New         }
  };

  ContainerConfig::InstallStatus
  extract_install_status_from_json(QJsonObject const& json_object)
  {
    QJsonValue value = json_object["installStatus"];
    if (value != QJsonValue::Undefined)
    {
      QJsonValue::Type value_type = value.type();
      if (value_type == QJsonValue::String)
      {
        QString s = value.toString();
        if (s.length() > 0)
        {
          for (auto const& name: install_status_names)
          {
            if (0 == s.compare(name.string, Qt::CaseInsensitive))
            {
              return name.enumeration;
            }
          }
        }
      }
    }
    return ContainerConfig::InstallStatus::New;
  }
} // anonymous namespace


ContainerConfig::
ContainerConfig(QObject* parent)
: QObject(parent)
{ }


ContainerConfig::
ContainerConfig(QString const& container_id,
                QString const& container_name,
                QString const& image_id,
                QObject*       parent)
: QObject(parent)
, container_id_(container_id)
, container_name_(container_name)
, image_id_(image_id)
, install_status_(InstallStatus::New)
{ }


ContainerConfig::
ContainerConfig(QJsonObject const& json_object,
                QObject*          parent)
: QObject(parent)
, container_id_(extract_container_id_from_json(json_object))
, container_name_(extract_container_name_from_json(json_object, container_id_))
, image_id_(extract_image_id_from_json(json_object, container_id_))
, install_status_(extract_install_status_from_json(json_object))
{ }


ContainerConfig::
~ContainerConfig()
{ }


QString const& ContainerConfig::
container_id() const
{ return container_id_; }


QString const& ContainerConfig::
name() const
{ return container_name_; }


void ContainerConfig::
name(QString const& name)
{
  container_name_ = name;
  emit nameChanged();
}


QString const& ContainerConfig::
image_id() const
{ return image_id_; }


ContainerConfig::InstallStatus ContainerConfig::
install_status() const
{ return install_status_; }


void ContainerConfig::
install_status(InstallStatus install_status)
{
  install_status_ = install_status;
  emit installStatusChanged();
}


QJsonObject ContainerConfig::
toJson() const
{
  QJsonObject json_object;
  json_object["id"] = container_id_;
  json_object["name"] = container_name_;
  json_object["image"] = image_id_;
  for (auto const& name: install_status_names)
  {
    if (install_status_ == name.enumeration)
    {
      json_object["installStatus"] = name.string;
    }
  }
  return json_object;
}


