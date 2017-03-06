/*
 * Copyright 2017 Canonical Ltd
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
#include "ContainersConfig.h"

#include <QJsonArray>
#include <QDebug>

namespace
{
QString translate_status(QString const& original)
{
  static const QMap<QString, QString> translations{
    {"new",                 QObject::tr("new")},
    {"installing",          QObject::tr("installing")},
    {"installed",           QObject::tr("installed")},
    {"installing packages", QObject::tr("installing packages")},
    {"removing packages",   QObject::tr("removing packages")},
    {"starting",            QObject::tr("starting")},
    {"running",             QObject::tr("running")},
    {"stopping",            QObject::tr("stopping")},
    {"stopped",             QObject::tr("stopped")},
    {"freezing",            QObject::tr("freezing")},
    {"frozen",              QObject::tr("frozen")},
    {"ready",               QObject::tr("ready")},
    {"updating",            QObject::tr("updating")},
    {"removing",            QObject::tr("removing")},
    {"removed",             QObject::tr("removed")},
    {"unknown",             QObject::tr("unknown")}
  };

  return translations.value(original, "");
}

QString try_get_string(QJsonObject object, QString const& key, QString fallback = "unknown")
{
  auto value = object.value(key);
  return value.isUndefined() ? fallback : value.toString();
}


bool try_get_bool(QJsonObject object, QString const& key)
{
  auto value = object.value(key);
  return value.isUndefined() ? false : value.toBool();
}
}


ContainersConfig::Container::Archive::
Archive(QJsonObject const& json)
: status_(try_get_string(json, "archiveStatus"))
, name(try_get_string(json, "archiveName"))
, status(translate_status(status_))
{ }


QJsonObject ContainersConfig::Container::Archive::
dump() const
{
  QJsonObject object;
  object["archiveName"] = name;
  object["archiveStatus"] = status_;

  return object;
}


ContainersConfig::Container::BindMount::
BindMount(QString const& json)
: path(json)
{ }


QString ContainersConfig::Container::BindMount::
dump() const
{
  return path;
}


ContainersConfig::Container::InstalledApp::
InstalledApp(QJsonObject const& json)
: status_(try_get_string(json, "appStatus"))
, name(try_get_string(json, "packageName"))
, status(translate_status(status_))
{ }


QJsonObject ContainersConfig::Container::InstalledApp::
dump() const
{
  QJsonObject object;
  object["packageName"] = name;
  object["appStatus"] = status_;

  return object;
}


ContainersConfig::Container::
Container(QString const& id, QString const& name, QString const& type,
          QString const& distro, QString const& status, QString const& multiarch,
          bool freeze)
  : status_(status)
  , name(name)
  , id(id)
  , distro(distro)
  , status(translate_status(status_))
  , type(type)
  , multiarch(multiarch)
  , freeze(freeze)
{ }


ContainersConfig::Container::
Container(QJsonObject const& json)
: Container(try_get_string(json, "id"), try_get_string(json, "name"), try_get_string(json, "type"),
            try_get_string(json, "distro"), try_get_string(json, "installStatus"),
            try_get_string(json, "multiarch", "disabled"), try_get_bool(json, "freezeOnStop"))
{
  for (auto const& archive: json["extraArchives"].toArray())
  {
    archives.append(Archive(archive.toObject()));
  }

  for (auto const& app: json["installedApps"].toArray())
  {
    installed_apps.append(InstalledApp(app.toObject()));
  }

  for (auto const& mount: json["bindMounts"].toArray())
  {
    mounts.append(BindMount(mount.toString()));
  }
}


QJsonObject ContainersConfig::Container::
dump() const
{
  QJsonObject object;
  object["name"] = name;
  object["id"] = id;
  object["distro"] = distro;
  object["installStatus"] = status_;
  object["multiarch"] = multiarch;
  object["type"] = type;
  object["freezeOnStop"] = freeze;

  QJsonArray archives_list;
  for (auto const& archive: archives)
  {
    archives_list.append(archive.dump());
  }
  object["extraArchives"] = archives_list;

  QJsonArray installed_apps_list;
  for (auto const& app: installed_apps)
  {
    installed_apps_list.append(app.dump());
  }
  object["installedApps"] = installed_apps_list;

  QJsonArray mounts_list;
  for (auto const& mount: mounts)
  {
    mounts_list.append(mount.dump());
  }
  object["bindMounts"] = mounts_list;

  return object;
}


ContainersConfig::
ContainersConfig(QJsonObject const& json)
: default_container(try_get_string(json, "defaultContainer", ""))
{
  for (auto const& container: json["containerList"].toArray())
  {
    containers.append(Container(container.toObject()));
  }
}


QJsonObject ContainersConfig::
dump() const
{
  QJsonObject object;
  object["defaultContainer"] = default_container;

  QJsonArray container_list;
  for (auto const& container: containers)
  {
    container_list.append(container.dump());
  }
  object["containerList"] = container_list;

  return object;
}
