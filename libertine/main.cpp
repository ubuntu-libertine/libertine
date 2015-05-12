/**
 * @file main.cpp
 * @brief Libertine app mainline driver.
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

#include <QDebug>
#include <QGuiApplication>
#include <QStringList>


int
main(int argc, char* argv[])
{
  QGuiApplication app(argc, argv);
  app.setApplicationVersion(LIBERTINE_VERSION);

  QStringList args = app.arguments();
  if (args.contains("-V") || args.contains("--version"))
  {
    qDebug() << app.applicationName() << " " << app.applicationVersion();
    return 0;
  }
  if (args.contains("-h") || args.contains("--help"))
  {
    qDebug() << "usage: " << args.at(0) << " [-h] [-v]";
    qDebug() << "  -V, --version\t print app version and exit";
    qDebug() << "  -h, --help\t print this help and exit";
    return 0;
  }

  return app.exec();
}
