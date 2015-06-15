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

#include <QtCore/QScopedPointer>
#include <QtCore/QString>
#include <QtGui/QGuiApplication>
#include <QtQuick/QQuickView>


class ContainerConfigList;
class LibertineConfig;


class Libertine
: public QGuiApplication
{
  Q_OBJECT

public:
    Libertine(int argc, char* argv[]);
    ~Libertine();

private:
    void
    initialize_view();

    void
    load_container_config_list();

    void
    save_container_config_list();

private slots:
    void
    handleContainerConfigsChanged();

private:
    QString                         main_qml_source_file_;
    QScopedPointer<LibertineConfig> config_;
    ContainerConfigList*            containers_;
    QQuickView                      view_;
};

#endif /* LIBERTINE_LIBERTINE_H */
