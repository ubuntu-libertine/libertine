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


static QString getPersistentSurfaceId(Display *dpy, const Window& id)
{
  Atom prop = XInternAtom(dpy, MIR_WM_PERSISTENT_ID, 0),
       type; // unused
  int form, // unused
      status;
  unsigned long remain, // unused
                len;    // unused
  unsigned char *data = nullptr;
  QString persistentSurfaceId;

  status = XGetWindowProperty(dpy, id, prop, 0, 1024, 0,
                              XA_STRING, &type, &form, &len, &remain, &data);

  if (status)
  {
    qDebug() << "Failure retrieving the persistentSurfaceID!";
  }
  else
  {
    persistentSurfaceId = (const char *)data;
  }

  XFree(data);

  return persistentSurfaceId;
}


Display *checkXServer()
{
  char *display = getenv("DISPLAY");

  if (display == nullptr)
  {
    qCritical() << "DISPLAY environment variable not set!";
    exit(-1);
  }

  Display *dpy = XOpenDisplay(display);
  if (dpy == nullptr)
  {
    qCritical() << "Xmir is not running on DISPLAY" << display << "!";
    exit(-1);
  }

  return dpy;
}

} //anonymous namespace


XEventWorker::
XEventWorker(Display *dpy)
: dpy_(dpy)
{
  unityFocus_ = new QDBusInterface(UNITY_FOCUSINFO_SERVICE,
                                   UNITY_FOCUSINFO_PATH,
                                   UNITY_FOCUSINFO_INTERFACE,
                                   QDBusConnection::sessionBus(),
                                   this);
}


XEventWorker::
~XEventWorker()
{
  XCloseDisplay(dpy_);
}


bool XEventWorker::
isSurfaceFocused(const Window& focus_window)
{
  surfaceId_ = getPersistentSurfaceId(dpy_, focus_window);

  QDBusReply<bool> isFocused = unityFocus_->call(UNITY_FOCUSINFO_METHOD, surfaceId_);

  return isFocused;
}


void XEventWorker::
checkForAppFocus()
{
  bool hasFocus = false;
  int focus_state;
  Window focus_window;

  XGetInputFocus(dpy_, &focus_window, &focus_state);

  if (focus_window > PointerRoot)
  {
    if (isSurfaceFocused(focus_window))
    {
      focusChanged(surfaceId_);
      hasFocus = true;
    }
  }

  XSelectInput(dpy_, XDefaultRootWindow(dpy_), FocusChangeMask);
  
  bool focused = false;
  XEvent event;

  while (1)
  {
    XNextEvent(dpy_, &event);

    XGetInputFocus(dpy_, &focus_window, &focus_state);

    if (focus_window > PointerRoot)
    {
      focused = isSurfaceFocused(focus_window);

      if (hasFocus == false && focused == true)
      {
        qDebug() << "Surface is focused";
        focusChanged(surfaceId_);
        hasFocus = true;
      }
      else if (hasFocus == true && focused == false)
      {
        qDebug() << "Surface lost focus";
        hasFocus = false;
      }
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
setPersistentSurfaceId(const QString& surfaceId)
{
  if (persistentSurfaceId_ != surfaceId)
  {
    persistentSurfaceId_ = surfaceId;
  }
}


void Pasted::
appFocused(const QString& surfaceId)
{
  setPersistentSurfaceId(surfaceId);
  handleContentHubPasteboard();
}


int
main(int argc, char* argv[])
{
  qSetMessagePattern(QString("%{appname}: %{message}"));

  Display *dpy = checkXServer();

  Pasted pasted(argc, argv);

  QThread t;
  XEventWorker worker(dpy);

  worker.moveToThread(&t);

  QObject::connect(&worker, &XEventWorker::focusChanged, &pasted, &Pasted::appFocused);
  QObject::connect(&t, &QThread::started, &worker, &XEventWorker::checkForAppFocus);

  t.start();
  
  return pasted.exec();
}
