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

#include <QtGui/QGuiApplication>
#include <QtQuick/QQuickView>


class Libertine
: public QGuiApplication
{
  Q_OBJECT

public:
    Libertine(int argc, char* argv[]);
    ~Libertine();

private:
    void
    parse_command_line();

    void
    initialize_view();

private:
    QQuickView  view_;
};

#endif /* LIBERTINE_LIBERTINE_H */
