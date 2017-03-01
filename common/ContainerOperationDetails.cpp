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


#include "ContainerOperationDetails.h"

ContainerOperationDetails::
ContainerOperationDetails(QObject* parent)
  : QObject(parent)
{
}


QString ContainerOperationDetails::
details(QString const& container_id) const
{
  return details_.value(container_id);
}


void ContainerOperationDetails::
clear(QString const& container_id)
{
  details_.remove(container_id);
}


void ContainerOperationDetails::
update(QString const& container_id, QString const& new_details)
{
  details_[container_id] += new_details;

  emit updated(container_id, new_details);
}
