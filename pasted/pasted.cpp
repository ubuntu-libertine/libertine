/*
 * @file pasted.cpp
 * @brief Copy & Paste daemon between X apps, other X apps, and native apps
 */
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

#include "pasted.h"

#include <QDBusInterface>
#include <QDebug>
#include <QThread>

#include <X11/Xatom.h>


namespace
{

constexpr auto MIR_WM_PERSISTENT_ID = "_MIR_WM_PERSISTENT_ID";
constexpr auto UNITY_FOCUSINFO_SERVICE = "com.canonical.Unity.FocusInfo";
constexpr auto UNITY_FOCUSINFO_PATH = "/com/canonical/Unity/FocusInfo";
constexpr auto UNITY_FOCUSINFO_INTERFACE = "com.canonical.Unity.FocusInfo";
constexpr auto UNITY_FOCUSINFO_METHOD = "isSurfaceFocused";


static QString getPersistentSurfaceId()
{
  Display *dpy  = XOpenDisplay(NULL);
  Atom prop = XInternAtom(dpy, MIR_WM_PERSISTENT_ID, 0),
       type; // unused
  int form, // unused
      status;
  unsigned long remain, // unused
                len;    // unused
  unsigned char *data = nullptr;
  QString persistentSurfaceId;

  status = XGetWindowProperty(dpy, XDefaultRootWindow(dpy), prop, 0, 1024, 0,
                              XA_STRING, &type, &form, &len, &remain, &data);

  if (status)
  {
    qDebug() << "Failure retrieving the persistentSurfaceID!";
  }
  else
  {
    persistentSurfaceId = (const char *)data;
  }

  XCloseDisplay(dpy);
  XFree(data);

  return persistentSurfaceId;
}

} //anonymous namespace


void XEventWorker::
checkForAppFocus()
{
  bool hasFocus = false;
  XEvent event;

  QDBusInterface *unityFocus = new QDBusInterface(UNITY_FOCUSINFO_SERVICE,
                                                  UNITY_FOCUSINFO_PATH,
                                                  UNITY_FOCUSINFO_INTERFACE,
                                                  QDBusConnection::sessionBus(),
                                                  this);

  QString surfaceId = getPersistentSurfaceId();

  QDBusReply<bool> isFocused = unityFocus->call(UNITY_FOCUSINFO_METHOD, surfaceId);

  if (isFocused == true)
  {
    focusChanged();
    hasFocus = true;
  }

  Display *dpy = XOpenDisplay(NULL);
  XSelectInput(dpy, XDefaultRootWindow(dpy), FocusChangeMask);
  
  while (1)
  {
    XNextEvent(dpy, &event);

    isFocused = unityFocus->call(UNITY_FOCUSINFO_METHOD, surfaceId);

    if (hasFocus == false && isFocused == true)
    {
      qDebug() << "Surface is focused";
      focusChanged();
      hasFocus = true;
    }
    else if (hasFocus == true && isFocused == false)
    {
      qDebug() << "Surface lost focus";
      hasFocus = false;
    }
  }
}


Pasted::
Pasted(int argc, char** argv)
: QApplication(argc, argv)
, clipboard_(QApplication::clipboard())
, content_hub_(cuc::Hub::Client::instance())
, mimeDataX_(new QMimeData)
, lastMimeData_()
{
  setApplicationName("pasted");

  connect(clipboard_, &QClipboard::dataChanged, this, &Pasted::handleXClipboard);
}


void Pasted::
handleXClipboard()
{
  qDebug() << "Change in X clipboard";

  const QMimeData *xClipboard = clipboard_->mimeData();

  if ((xClipboard == nullptr) || xClipboard->formats().empty())
  {
    qDebug() << "Empty xClipboard.  Not setting pasteboard.";
  }
  else if (!compareMimeData(xClipboard, lastMimeData_.get()))
  {
    qDebug() << "X clipboard data is different";
    updateLastMimeData(xClipboard);
 
    content_hub_->createPasteSync(persistentSurfaceId_, *lastMimeData_);
  }
}


void Pasted::
handleContentHubPasteboard()
{
  const QMimeData *pasteboard = content_hub_->latestPaste(persistentSurfaceId_);

  if (!compareMimeData(pasteboard, lastMimeData_.get()))
  {
    qDebug() << "content-hub pasteboard data is different";
    updateXMimeData(pasteboard);

    clipboard_->setMimeData(mimeDataX_);
  }
}


bool Pasted::
compareMimeData(const QMimeData *a, const QMimeData *b)
{
  if ((a == nullptr) || (b == nullptr))
  {
    return false;
  }

  if (a->formats() != b->formats())
  {
    return false;
  }

  for (const QString& formatName: a->formats())
  {
    if (a->data(formatName) != b->data(formatName))
    {
      return false;
    }
  }

  return true;
}


void Pasted::
copyMimeData(QMimeData& target, const QMimeData *source)
{
  if (source == nullptr)
  {
    qDebug() << "Copy source is null!";
    return;
  }

  for (const QString& format : source->formats())
  {
    // Need to filter out these Mime types due to The Gimp crashing when copying these types
    if (format != "image/x-MS-bmp" && format != "image/x-bmp")
    {
      target.setData(format, source->data(format));
    }
  }
}


void Pasted::
updateLastMimeData(const QMimeData *source)
{
  lastMimeData_.reset(new QMimeData);

  copyMimeData(*lastMimeData_.get(), source);
}


void Pasted::
updateXMimeData(const QMimeData *source)
{
  updateLastMimeData(source);

  mimeDataX_ = new QMimeData;
  copyMimeData(*mimeDataX_, source);
}


void Pasted::
setPersistentSurfaceId()
{
  if (persistentSurfaceId_.isEmpty())
  {
    persistentSurfaceId_ = getPersistentSurfaceId();
  }
}


void Pasted::
appFocused()
{
  setPersistentSurfaceId();
  handleContentHubPasteboard();
}


int
main(int argc, char* argv[])
{
  qSetMessagePattern(QString("%{appname}: %{message}"));

  Pasted pasted(argc, argv);

  QThread t;
  XEventWorker worker;

  worker.moveToThread(&t);

  QObject::connect(&worker, &XEventWorker::focusChanged, &pasted, &Pasted::appFocused);
  QObject::connect(&t, &QThread::started, &worker, &XEventWorker::checkForAppFocus);

  t.start();
  
  return pasted.exec();
}
