/*
 * Copyright 2016 Canonical Ltd
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


#include "PackageOperationDetails.h"

namespace
{
static bool has_key(QMap<QString, QMap<QString, QString> > details,
                    QString const& container_id, QString const& package_id)
{
  return details.constFind(container_id) != details.constEnd() &&
      details[container_id].constFind(package_id) != details[container_id].constEnd();
}
}


PackageOperationDetails::
PackageOperationDetails(QObject* parent)
  : QObject(parent)
{
}


QString PackageOperationDetails::
details(QString const& container_id, QString const& package_id) const
{
  if (has_key(details_, container_id, package_id))
  {
    return details_[container_id][package_id];
  }
  return "";
}


void PackageOperationDetails::
clear(QString const& container_id, QString const& package_id)
{
  if (has_key(details_, container_id, package_id))
  {
    details_[container_id].remove(package_id);
    if (details_[container_id].empty())
    {
      details_.remove(container_id);
    }
  }
}


void PackageOperationDetails::
update(QString const& container_id, QString const& package_id, QString const& new_details)
{
  if (has_key(details_, container_id, package_id))
  {
    details_[container_id][package_id] += new_details;
  }
  else
  {
    if (details_.constFind(container_id) == details_.constEnd())
    {
      details_[container_id] = QMap<QString, QString>{{package_id, new_details}};
    }
  }

  emit updated(container_id, package_id, new_details);
}
