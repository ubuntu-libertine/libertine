/*
 * Copyright 2016-2017 Canonical Ltd
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

#include <QObject>
#include <QMap>


class ContainerOperationDetails : public QObject
{
  Q_OBJECT

public:
  explicit ContainerOperationDetails(QObject* parent = nullptr);
  virtual ~ContainerOperationDetails() = default;

  Q_INVOKABLE QString details(QString const& container_id) const;
  Q_INVOKABLE void clear(QString const& container_id);

public slots:
  void update(QString const& container_id, QString const& new_details);

signals:
  void updated(QString const& container_id, QString const& new_details);
  void send(QString const& input);
  void error(QString const& short_description, QString const& details);

private:
  QMap<QString, QString> details_;
};
