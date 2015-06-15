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
#include "libertine/ContainerConfig.h"
#include "libertine/ContainerConfigList.h"
#include "libertine/libertine.h"
#include "libertine/LibertineConfig.h"
#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QFileInfo>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonObject>
#include <QtCore/QJsonParseError>
#include <QtCore/QStandardPaths>
#include <QtQml/QQmlContext>
#include <QtQml/QQmlEngine>


namespace
{
static QString const s_main_QML_source_file = "qml/libertine.qml";

/**
 * Searches for the main QML source file.
 *
 * The actual QML sources could be in any of a number of places depending on if
 * the program was invoked from within the developer's source tree, a DEB, a
 * click, a clack, a snap or a snood.  Gotta check 'em all, in some semblance
 * of a priority order in which the developer's source tree is highest priority
 * and the system installation places are lowest.
 *
 * @returns the source file path or an empty string if no source file was found.
 */
static QString
find_main_qml_source_file()
{
  static const QStringList sub_paths = { "", "libertine/" };
  QStringList paths = QStandardPaths::standardLocations(QStandardPaths::DataLocation);
  paths.prepend(QDir::currentPath());
  paths.prepend(QCoreApplication::applicationDirPath());
  for (auto const& path: paths)
  {
    for (auto const& sub: sub_paths)
    {
      QFileInfo fi(path + "/" + sub + s_main_QML_source_file);
      if (fi.exists())
      {
        return fi.filePath();
      }
    }
  }
  return QString();
}

} // anonymous namespace


/**
 * Constraucts a Libertine application wrapper object.
 * @param[in] argc  The count of the number of command-line arguments.
 * @param[in] argv  A vector of command-line arguments.
 *
 * Sets up the Libertine application from the command-line arguments,
 * environment variables, and configurations files and displays the GUI.
 */
Libertine::
Libertine(int argc, char* argv[])
: QGuiApplication(argc, argv)
, main_qml_source_file_(find_main_qml_source_file())
{
  setApplicationName(LIBERTINE_APPLICATION_NAME);
  setApplicationVersion(LIBERTINE_VERSION);
  config_.reset(new LibertineConfig(*this));
  qmlRegisterType<ContainerConfig>("Libertine", 1, 0, "ContainerConfig");

  if (main_qml_source_file_.isEmpty())
  {
    qWarning() << "Can not locate " << s_main_QML_source_file;
  }

  load_container_config_list();

  initialize_view();
  view_.show();
}


/**
 * Tears diwn the Libertine application wrapper object.
 */
Libertine::
~Libertine()
{
}


/**
 * Initializes the main QML view.
 */
void Libertine::
initialize_view()
{
  view_.setResizeMode(QQuickView::SizeRootObjectToView);
  QQmlContext* ctxt = view_.rootContext();
  ctxt->setContextProperty("containerConfigList", containers_);

  view_.setSource(QUrl::fromLocalFile(main_qml_source_file_));
  connect(view_.engine(), SIGNAL(quit()), SLOT(quit()));
}


void Libertine::
load_container_config_list()
{
  QFile config_file(config_->containers_config_file_name());
  if (config_file.exists())
  {
    if (!config_file.open(QIODevice::ReadOnly))
    {
      qWarning() << "could not open containers config file " << config_file.fileName();
      containers_ = new ContainerConfigList(this);
    } else {
      QJsonParseError parse_error;
      QJsonDocument json = QJsonDocument::fromJson(config_file.readAll(), &parse_error);
      if (parse_error.error)
      {
        qWarning() << "error parsing containers config file: " << parse_error.errorString();
      }
      containers_ = new ContainerConfigList(json.object(), this);
    }
  } else {
    containers_ = new ContainerConfigList(this);
  }
}

