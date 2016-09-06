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

#include <QDebug>

#include <QX11Info>
#include <X11/Xatom.h>


Pasted::
Pasted(int argc, char** argv)
: QApplication(argc, argv)
, clipboard_(QApplication::clipboard())
, content_hub_(cuc::Hub::Client::instance())
, mimeDataX_(new QMimeData)
, lastMimeData_()
, rootWindowHasFocus_(false)
, firstSeenWindow_(None)
{
  setApplicationName("pasted");

  QTimer *timer = new QTimer(this);
  connect(timer, &QTimer::timeout, this, &Pasted::checkForAppFocus);
  timer->start(400);

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


void Pasted::
checkForAppFocus()
{
  Window w;
  int revert_to; // unused

  XGetInputFocus(QX11Info::display(), &w, &revert_to);

  if (firstSeenWindow_ == None && w != None)
  {
    firstSeenWindow_ = w;
  }

  if (w == None && rootWindowHasFocus_ == true)
  {
    qDebug() << "Xmir lost focus";
    rootWindowHasFocus_ = false;
  }
  else if ((w == PointerRoot ||
           (w && firstSeenWindow_ == PointerRoot))
           && rootWindowHasFocus_ == false)
  {
    qDebug() << "Xmir gained focus";
    rootWindowHasFocus_ = true;
    setPersistentSurfaceId();
    handleContentHubPasteboard();
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
    Atom prop = XInternAtom(QX11Info::display(), "_MIR_WM_PERSISTENT_ID", 0),
         type; // unused
    int form, // unused
        status;
    unsigned long remain, // unused
                  len;    // unused
    unsigned char *data;
    status = XGetWindowProperty(QX11Info::display(), XDefaultRootWindow(QX11Info::display()), prop,
                                0, 1024, 0, XA_STRING, &type, &form, &len, &remain, &data);

    if (status)
    {
      qDebug() << "Failure retrieving the persistentSurfaceID!";
    }
    else
    {
      qDebug() << "Setting persistentSurfaceId";
      persistentSurfaceId_ = (const char *)data;
    }
  }
}


int
main(int argc, char* argv[])
{
  qSetMessagePattern(QString("%{appname}: %{message}"));

  Pasted pasted(argc, argv);

  pasted.exec();
}
