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
#pragma once

#include <QList>
#include <QJsonObject>

class ContainersConfig
{
public:
  explicit ContainersConfig() = default;
  explicit ContainersConfig(QJsonObject const& json);
  virtual ~ContainersConfig() = default;

  QJsonObject dump() const;

  class Container
  {
  public:
    explicit Container(QJsonObject const& json);
    explicit Container(QString const& id = "unknown",
                       QString const& name = "unknown",
                       QString const& type = "unknown",
                       QString const& distro = "unknown",
                       QString const& status = "unknown",
                       QString const& multiarch = "disabled");
    virtual ~Container() = default;

    QJsonObject dump() const;

    class InstalledApp
    {
    public:
      explicit InstalledApp(QJsonObject const& json);
      virtual ~InstalledApp() = default;

      QJsonObject dump() const;

    private:
      QString status_; // untranslated

    public:
      QString name;
      QString status;
    };


    class Archive
    {
    public:
      explicit Archive(QJsonObject const& json);
      virtual ~Archive() = default;

      QJsonObject dump() const;

    private:
      QString status_; // untranslated

    public:
      QString name;
      QString status;
    };

  private:
    QString status_; // untranslated

  public:
    QString             name;
    QString             id;
    QString             distro;
    QString             status;
    QString             type;
    QString             multiarch;
    QList<Archive>      archives;
    QList<InstalledApp> installed_apps;
  };

  QList<Container> containers;
  QString          default_container;
};
