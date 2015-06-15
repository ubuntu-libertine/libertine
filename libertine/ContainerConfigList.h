/**
 * @file ContainerConfigList.h
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
#ifndef CONTAINER_CONTAINERCONFIGLIST_H
#define CONTAINER_CONTAINERCONFIGLIST_H

#include <QtCore/QJsonObject>
#include <QtCore/QList>
#include <QtCore/QObject>


class ContainerConfig;


/**
 * The runtime configuration of the Libertine tools.
 */
class ContainerConfigList
: public QObject
{
  Q_OBJECT

public:
  using ConfigList = QList<ContainerConfig*>;
  using iterator = ConfigList::iterator;
  using size_type = ConfigList::size_type;

  static const QString Json_object_name;

public:
  explicit
  ContainerConfigList(QObject* parent = nullptr);

  ContainerConfigList(QJsonObject const& json_object,
                      QObject*           parent = nullptr);

  ~ContainerConfigList();

  bool
  empty() const noexcept;

  size_type
  size() const noexcept;

private:
  ConfigList configs_;
};

#endif /* CONTAINER_CONTAINERCONFIGLIST_H */
