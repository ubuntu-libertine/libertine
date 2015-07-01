#ifndef LIBERTINE_PASSWORD_HELPER_H_
#define LIBERTINE_PASSWORD_HELPER_H_

#include <iostream>
#include <security/pam_appl.h>
#include <QtCore/QString>

class PasswordHelper
{
public:
  PasswordHelper();
  ~PasswordHelper();

  QString
  GetPassword();

  bool
  VerifyUserPassword(QString const& password);
};

#endif /* LIBERTINE_PASSWORD_HELPER_H_ */
