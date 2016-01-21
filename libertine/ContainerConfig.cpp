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

#include <QtCore/QDebug>
#include <QtCore/QJsonArray>
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
  extract_container_type_from_json(QJsonObject const& json_object,
                                   QString const&     container_id)
  {
    QString type = container_id;
    QJsonValue value = json_object["type"];
    if (value != QJsonValue::Undefined)
    {
      QJsonValue::Type value_type = value.type();
      if (value_type == QJsonValue::String)
      {
        QString s = value.toString();
        if (s.length() > 0)
        {
          type = s;
        }
      }
    }

    return type;
  }

  QString
  extract_distro_series_from_json(QJsonObject const& json_object,
                                  QString const&     container_id)
  {
    QString distro_series = container_id;
    QJsonValue value = json_object["distro"];
    if (value != QJsonValue::Undefined)
    {
      QJsonValue::Type value_type = value.type();
      if (value_type == QJsonValue::String)
      {
        QString s = value.toString();
        if (s.length() > 0)
        {
          distro_series = s;
        }
      }
    }

    return distro_series;
  }

  const static struct { QString string; ContainerConfig::InstallStatus enumeration; } install_status_names[] =
  {
    { QObject::tr("new"),          ContainerConfig::InstallStatus::New        },
    { QObject::tr("installing"),   ContainerConfig::InstallStatus::Installing },
    { QObject::tr("ready"),        ContainerConfig::InstallStatus::Ready      },
    { QObject::tr("removing"),     ContainerConfig::InstallStatus::Removing   },
    { QObject::tr("removed"),      ContainerConfig::InstallStatus::Removed    },
    { QObject::tr("failed"),       ContainerConfig::InstallStatus::Failed     },
    { QString(),                   ContainerConfig::InstallStatus::New        }
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

  const static struct { QString string; ContainerApps::AppStatus enumeration; } app_status_names[] =
  {
    { QObject::tr("new"),        ContainerApps::AppStatus::New        },
    { QObject::tr("installing"), ContainerApps::AppStatus::Installing },
    { QObject::tr("installed"),  ContainerApps::AppStatus::Installed  },
    { QObject::tr("failed"),     ContainerApps::AppStatus::Failed     },
    { QObject::tr("removing"),   ContainerApps::AppStatus::Removing   },
    { QObject::tr("removed"),    ContainerApps::AppStatus::Removed    },
    { QString(),                 ContainerApps::AppStatus::New        }
  };

  QString
  extract_package_name_from_json(QJsonObject const& json_object)
  {
    QString package_name;

    QJsonValue value = json_object["packageName"];
    if (value != QJsonValue::Undefined)
    {
      QJsonValue::Type value_type = value.type();
      if (value_type == QJsonValue::String)
      {
        package_name = value.toString();
      }
    }

    return package_name;
  }

  ContainerApps::AppStatus
  extract_app_status_from_json(QJsonObject const& json_object)
  {
    ContainerApps::AppStatus app_status = ContainerApps::AppStatus::New;

    QJsonValue value = json_object["appStatus"];
    if (value != QJsonValue::Undefined)
    {
      QJsonValue::Type value_type = value.type();
      if (value_type == QJsonValue::String)
      {
        QString s = value.toString();
        if (s.length() > 0)
        {
          for (auto const& name: app_status_names)
          {
            if (0 == s.compare(name.string, Qt::CaseInsensitive))
            {
              app_status = name.enumeration;
              break;
            }
          }
        }
      }
    }

    return app_status;
  }

  QList<ContainerApps*>
  extract_container_apps_from_json(QJsonObject const& json_object)
  {
    QList<ContainerApps*> container_apps;
    QString package_name;
    ContainerApps::AppStatus app_status;

    QJsonArray installed_apps = json_object["installedApps"].toArray();

    for (auto const& app: installed_apps)
    {
      package_name = extract_package_name_from_json(app.toObject());

      app_status = extract_app_status_from_json(app.toObject());

      container_apps.append(new ContainerApps(package_name, app_status));
    }
    return container_apps;
  }
} // anonymous namespace


ContainerApps::
ContainerApps(QString const& package_name,
              ContainerApps::AppStatus app_status,
              QObject* parent)
: QObject(parent)
, package_name_(package_name)
, app_status_(app_status)
{ }


ContainerApps::
~ContainerApps()
{ }


QString const& ContainerApps::
package_name() const
{ return package_name_; }


QString const& ContainerApps::
app_status() const
{ return app_status_names[(int)app_status_].string; }


ContainerConfig::
ContainerConfig(QObject* parent)
: QObject(parent)
{ }


ContainerConfig::
ContainerConfig(QString const& container_id,
                QString const& container_name,
                QString const& container_type,
                QString const& distro_series,
                QObject*       parent)
: QObject(parent)
, container_id_(container_id)
, container_name_(container_name)
, container_type_(container_type)
, distro_series_(distro_series)
, install_status_(InstallStatus::New)
{ }



ContainerConfig::
ContainerConfig(QJsonObject const& json_object,
                QObject*          parent)
: QObject(parent)
, container_id_(extract_container_id_from_json(json_object))
, container_name_(extract_container_name_from_json(json_object, container_id_))
, container_type_(extract_container_type_from_json(json_object, container_id_))
, distro_series_(extract_distro_series_from_json(json_object, container_id_))
, install_status_(extract_install_status_from_json(json_object))
, container_apps_(extract_container_apps_from_json(json_object))
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
container_type() const
{ return container_type_; }


QString const& ContainerConfig::
distro_series() const
{ return distro_series_; }


QString const& ContainerConfig::
install_status() const
{ return install_status_names[(int)install_status_].string; }


void ContainerConfig::
install_status(InstallStatus install_status)
{
  install_status_ = install_status;
  emit installStatusChanged();
}


QList<ContainerApps*> & ContainerConfig::
container_apps()
{ return container_apps_; }


QJsonObject ContainerConfig::
toJson() const
{
  QJsonObject json_object,
              app_object;
  QJsonArray apps;

  json_object["id"] = container_id_;
  json_object["name"] = container_name_;
  json_object["type"] = container_type_;
  json_object["distro"] = distro_series_;
  for (auto const& name: install_status_names)
  {
    if (install_status_ == name.enumeration)
    {
      json_object["installStatus"] = name.string;
      break;
    }
  }
  for (auto const& container_app: container_apps_)
  {
    app_object["packageName"] = container_app->package_name();
    app_object["appStatus"] = app_status_names[0].string;
    apps.append(app_object);
  }
  json_object["installedApps"] = apps;

  return json_object;
}
