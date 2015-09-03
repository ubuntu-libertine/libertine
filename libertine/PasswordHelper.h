/**
 * @file PasswordHelper.h
 * @brief Helper class for managing password entry
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
#ifndef LIBERTINE_PASSWORD_HELPER_H_
#define LIBERTINE_PASSWORD_HELPER_H_

#include <iostream>
#include <security/pam_appl.h>
#include <QtCore/QObject>
#include <QtCore/QString>

class PasswordHelper
: public QObject
{
  Q_OBJECT

public:
  PasswordHelper();
  ~PasswordHelper();

  QString
  GetPassword();

  Q_INVOKABLE bool
  VerifyUserPassword(QString const& password);
};

#endif /* LIBERTINE_PASSWORD_HELPER_H_ */
