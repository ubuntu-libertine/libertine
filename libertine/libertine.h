/**
 * @file libertine.h
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
#ifndef LIBERTINE_LIBERTINE_H
#define LIBERTINE_LIBERTINE_H

#include <QtCore/QFileSystemWatcher>
#include <QtCore/QScopedPointer>
#include <QtCore/QString>
#include <QtGui/QGuiApplication>
#include <QtQuick/QQuickView>


class ContainerConfigList;
class LibertineConfig;
class ContainerAppsList;
class ContainerArchivesList;
class ContainerBindMountsList;
class PackageOperationDetails;


class Libertine
: public QGuiApplication
{
  Q_OBJECT

public:
    Libertine(int& argc, char** argv);
    ~Libertine();

private:
    void
    initialize_view();

private slots:
    void
    reload_config(const QString& path);

private:
    QString                         main_qml_source_file_;
    QScopedPointer<LibertineConfig> config_;
    QFileSystemWatcher              watcher_;
    ContainerConfigList*            containers_;
    ContainerAppsList*              container_apps_;
    ContainerArchivesList*          container_archives_;
    ContainerBindMountsList*        container_bind_mounts_;
    PackageOperationDetails*        package_operation_details_;
    QQuickView                      view_;
};

#endif /* LIBERTINE_LIBERTINE_H */
