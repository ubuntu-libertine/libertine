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
