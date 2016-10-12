/*
 * Copyright (C) 2016 Canonical Ltd.
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License version 3, as published
 * by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranties of
 * MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
 * PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "plugin.h"

#include "config.h"
#include "common/ContainerManager.h"
#include "common/ContainerAppsList.h"
#include "common/ContainerArchivesList.h"
#include "common/ContainerConfigList.h"
#include "common/LibertineConfig.h"
#include "common/ContainerConfig.h"
#include "common/PackageOperationDetails.h"
#include <memory>
#include <QQmlEngine>
#include <QQmlContext>
#include <QFileSystemWatcher>
#include <SystemSettings/ItemBase>

using namespace SystemSettings;

class LibertineItem: public ItemBase
{
    Q_OBJECT

public:
    explicit LibertineItem(const QVariantMap &staticData, QObject *parent = 0);
    virtual ~LibertineItem() = default;

    virtual QQmlComponent* pageComponent(QQmlEngine *engine,
                                         QObject *parent = 0) override;

private:
    std::unique_ptr<LibertineConfig> config_;
    ContainerConfigList*            containers_;
    ContainerAppsList*              container_apps_;
    ContainerArchivesList*          container_archives_;
    PackageOperationDetails*        package_operation_details_;
    QFileSystemWatcher              watcher_;

private slots:
    void reload_config(QString const&);
};

LibertineItem::
LibertineItem(const QVariantMap &staticData, QObject *parent)
  : ItemBase(staticData, parent)
  , config_(new LibertineConfig())
  , containers_(new ContainerConfigList(config_.get(), this))
  , container_apps_(new ContainerAppsList(containers_, this))
  , container_archives_(new ContainerArchivesList(containers_, this))
  , package_operation_details_(new PackageOperationDetails(this))
  , watcher_({config_->containers_config_file_name()})
{
  qmlRegisterType<ContainerConfig>("Libertine", 1, 0, "ContainerConfig");
  qmlRegisterType<ContainerManagerWorker>("Libertine", 1, 0, "ContainerManagerWorker");
  qmlRegisterType<PackageOperationDetails>("Libertine", 1, 0, "PackageOperationDetails");

  connect(&watcher_, &QFileSystemWatcher::fileChanged, this, &LibertineItem::reload_config);
}

QQmlComponent *LibertineItem::
pageComponent(QQmlEngine *engine, QObject *parent)
{
  auto ctxt = engine->rootContext();
  ctxt->setContextProperty("containerConfigList", containers_);
  ctxt->setContextProperty("containerAppsList", container_apps_);
  ctxt->setContextProperty("containerArchivesList", container_archives_);
  ctxt->setContextProperty("packageOperationDetails", package_operation_details_);

  auto component = new QQmlComponent(engine,
                           QUrl(LIBERTINE_PLUGIN_QML_DIR "/MainSettingsPage.qml"),
                           parent);
  return component;
}


void LibertineItem::
reload_config(QString const&)
{
  containers_->reloadConfigs();
}


ItemBase *LibertinePlugin::
createItem(const QVariantMap &staticData,
                                 QObject *parent)
{
  return new LibertineItem(staticData, parent);
}

#include "plugin.moc"
