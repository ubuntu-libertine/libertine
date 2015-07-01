#include "libertine/PasswordHelper.h"

#include <iostream>
#include <termios.h>
#include <unistd.h>

using namespace std;

namespace
{

struct pam_response *reply;

int function_conversation(int num_msg, const struct pam_message **msg, struct pam_response **resp, void *appdata_ptr)
{
  *resp = reply;
  return PAM_SUCCESS;
}

void set_stdin_echo(bool enable = true)
{
  struct termios tty;

  tcgetattr(STDIN_FILENO, &tty);
  if (!enable)
      tty.c_lflag &= ~ECHO;
  else
      tty.c_lflag |= ECHO;

  (void) tcsetattr(STDIN_FILENO, TCSANOW, &tty);
}

}  // anonymous namespace


PasswordHelper::
PasswordHelper()
{
}


PasswordHelper::
~PasswordHelper()
{
}


QString PasswordHelper::
GetPassword()
{
  string password;

  cout << "Please enter your password:" << endl;

  set_stdin_echo(false);
  getline(cin, password);
  set_stdin_echo(true);

  if (cin.fail() || cin.eof())
  {
    return nullptr;
  }
  else
  {
    return QString::fromStdString(password);
  }
}


bool PasswordHelper::
VerifyUserPassword(QString const& password)
{
  char *username = getenv("USER");
  int retval;

  const struct pam_conv local_conversation = { function_conversation, NULL };
  pam_handle_t *local_auth_handle = NULL;

  retval = pam_start("common_auth", username, &local_conversation, &local_auth_handle);

  if (retval != PAM_SUCCESS)
  {
    return false;
  }

  reply = (struct pam_response *)malloc(sizeof(struct pam_response));

  reply[0].resp = strdup(password.toStdString().c_str());
  reply[0].resp_retcode = 0;

  retval = pam_authenticate(local_auth_handle, 0);

  if (retval != PAM_SUCCESS)
  {
    return false;
  }

  retval = pam_end(local_auth_handle, retval);

  if (retval != PAM_SUCCESS)
  {
    return false;
  }
  return true;
}
