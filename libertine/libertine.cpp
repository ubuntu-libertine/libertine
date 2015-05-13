/**
 * @file libertine.cpp
 * @brief Libertine app wrapper
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
#include "libertine/config.h"

#include <cstdlib>
#include "libertine/libertine.h"
#include <QtCore/QDebug>
#include <QtQml/QQmlEngine>


Libertine::
Libertine(int argc, char* argv[])
: QGuiApplication(argc, argv)
{
  setApplicationVersion(LIBERTINE_VERSION);
  parse_command_line();
  initialize_view();
  view_.show();
}


Libertine::
~Libertine()
{
}


void Libertine::
parse_command_line()
{
  for (auto const& arg: arguments())
  {
    if (arg == "-V" || arg == "--version")
    {
      qDebug() << applicationName() << " " << applicationVersion();
      std::exit(0);
    }
    if (arg == "-h" || arg == "--help")
    {
      qDebug() << "usage: " << arguments().at(0) << " [-h] [-v]";
      qDebug() << "  -V, --version\t print app version and exit";
      qDebug() << "  -h, --help\t print this help and exit";
      std::exit(0);
    }
  }
}


void Libertine::
initialize_view()
{
  view_.setResizeMode(QQuickView::SizeRootObjectToView);
  view_.setSource(QUrl::fromLocalFile("qml/libertine.qml"));
  connect((QObject*)view_.engine(), SIGNAL(quit()), SLOT(quit()));
}


