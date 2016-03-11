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

  QString
  extract_multiarch_support_from_json(QJsonObject const& json_object)
  {
    QString multiarch_support("disabled");
    QJsonValue value = json_object["multiarch"];
    if (value != QJsonValue::Undefined)
    {
      QJsonValue::Type value_type = value.type();
      if (value_type == QJsonValue::String)
      {
        QString s = value.toString();
        if (s.length() > 0)
        {
          multiarch_support = s;
        }
      }
    }

    return multiarch_support;
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

  const static struct { QString string; CurrentStatus enumeration; } status_names[] =
  {
    { QObject::tr("new"),        CurrentStatus::New        },
    { QObject::tr("installing"), CurrentStatus::Installing },
    { QObject::tr("installed"),  CurrentStatus::Installed  },
    { QObject::tr("failed"),     CurrentStatus::Failed     },
    { QObject::tr("removing"),   CurrentStatus::Removing   },
    { QObject::tr("removed"),    CurrentStatus::Removed    },
    { QString(),                 CurrentStatus::New        }
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

  CurrentStatus
  extract_app_status_from_json(QJsonObject const& json_object)
  {
    CurrentStatus app_status = CurrentStatus::New;

    QJsonValue value = json_object["appStatus"];
    if (value != QJsonValue::Undefined)
    {
      QJsonValue::Type value_type = value.type();
      if (value_type == QJsonValue::String)
      {
        QString s = value.toString();
        if (s.length() > 0)
        {
          for (auto const& name: status_names)
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
    CurrentStatus app_status;

    QJsonArray installed_apps = json_object["installedApps"].toArray();

    for (auto const& app: installed_apps)
    {
      package_name = extract_package_name_from_json(app.toObject());

      app_status = extract_app_status_from_json(app.toObject());

      container_apps.append(new ContainerApps(package_name, app_status));
    }
    return container_apps;
  }

  QString
  extract_archive_name_from_json(QJsonObject const& json_object)
  {
    QString archive_name;

    QJsonValue value = json_object["archiveName"];
    if (value != QJsonValue::Undefined)
    {
      QJsonValue::Type value_type = value.type();
      if (value_type == QJsonValue::String)
      {
        archive_name = value.toString();
      }
    }

    return archive_name;
  }

  CurrentStatus
  extract_archive_status_from_json(QJsonObject const& json_object)
  {
    CurrentStatus archive_status = CurrentStatus::New;

    QJsonValue value = json_object["archiveStatus"];
    if (value != QJsonValue::Undefined)
    {
      QJsonValue::Type value_type = value.type();
      if (value_type == QJsonValue::String)
      {
        QString s = value.toString();
        if (s.length() > 0)
        {
          for (auto const& name: status_names)
          {
            if (0 == s.compare(name.string, Qt::CaseInsensitive))
            {
              archive_status = name.enumeration;
              break;
            }
          }
        }
      }
    }

    return archive_status;
  }

  QList<ContainerArchives*>
  extract_container_archives_from_json(QJsonObject const& json_object)
  {
    QList<ContainerArchives*> container_archives;
    QString archive_name;
    CurrentStatus archive_status;

    QJsonArray extra_archives = json_object["extraArchives"].toArray();

    for (auto const& archive: extra_archives)
    {
      archive_name = extract_archive_name_from_json(archive.toObject());
      archive_status = extract_archive_status_from_json(archive.toObject());

      container_archives.append(new ContainerArchives(archive_name, archive_status));
    }
    return container_archives;
  }
} // anonymous namespace


ContainerApps::
ContainerApps(QString const& package_name,
              CurrentStatus app_status,
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
{ return status_names[(int)app_status_].string; }


ContainerArchives::
ContainerArchives(QString const& archive_name,
                  CurrentStatus archive_status,
                  QObject* parent)
: QObject(parent)
, archive_name_(archive_name)
, archive_status_(archive_status)
{ }


ContainerArchives::
~ContainerArchives()
{ }


QString const& ContainerArchives::
archive_name() const
{ return archive_name_; }


QString const& ContainerArchives::
archive_status() const
{ return status_names[(int)archive_status_].string; }


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
, multiarch_support_(extract_multiarch_support_from_json(json_object))
, install_status_(extract_install_status_from_json(json_object))
, container_apps_(extract_container_apps_from_json(json_object))
, container_archives_(extract_container_archives_from_json(json_object))
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
multiarch_support() const
{ return multiarch_support_; }


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


QList<ContainerArchives*> & ContainerConfig::
container_archives()
{ return container_archives_; }


QJsonObject ContainerConfig::
toJson() const
{
  QJsonObject json_object,
              app_object,
              archive_object;
  QJsonArray apps,
             archives;

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
    app_object["appStatus"] = status_names[0].string;
    apps.append(app_object);
  }
  json_object["installedApps"] = apps;

  for (auto const& container_archive: container_archives_)
  {
    archive_object["archiveName"] = container_archive->archive_name();
    archives.append(archive_object);
  }
  json_object["extraArchives"] = archives;

  return json_object;
}
