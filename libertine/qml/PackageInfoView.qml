/**
 * @file PackageInfoView.qml
 * @brief Container package info view
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
import Libertine 1.0
import QtQuick 2.4
import QtQuick.Layouts 1.0
import Ubuntu.Components 1.2
import Ubuntu.Components.ListItems 1.2 as ListItem


Page {
    id: packageInfoView
    title: i18n.tr("Information for the %1 package").arg(mainView.currentPackage)
    property string currentContainer: mainView.currentContainer
    property var currentPackage: mainView.currentPackage
    property var statusText: containerConfigList.getAppStatus(currentContainer, currentPackage)
    property var failureReasonText: ""
    property var packageVersionText: i18n.tr("Obtaining package version…")
    property var worker: null
    property var install_signal: null


    Flickable {
        anchors.fill: parent
        contentHeight: contentItem.childrenRect.height
        boundsBehavior: (contentHeight > packageInfoView.height) ?
                            Flickable.DragAndOvershootBounds :
                            Flickable.StopAtBounds
        flickableDirection: Flickable.VerticalFlick

        Column {
            anchors.left: parent.left
            anchors.right: parent.right

            ListItem.Standard {
                text: i18n.tr("Package version")
                control: Label {
                    text: packageVersionText
                }
            }

            ListItem.Standard {
                text: i18n.tr("Install status")
                control: Label {
                    text: statusText
                }
            }

            ListItem.Standard {
                id: failureReason
                text: i18n.tr("Failure reason")
                visible: false
                control: Label {
                    text: failureReasonText
                    wrapMode: Text.Wrap
                    width: parent.parent.width/2
                    horizontalAlignment: Qt.AlignRight
                    onHeightChanged: updateFailureReasonHeight()
                }
            }
        }
    }

    Component.onCompleted: {
        if (install_signal) {
            install_signal.connect(installFinished)
        }
        containerConfigList.configChanged.connect(reloadStatus)
        var command = "apt-cache policy " + currentPackage
        var comp = Qt.createComponent("ContainerManager.qml")
        worker = comp.createObject(mainView, {"containerAction": ContainerManagerWorker.Exec,
                                              "containerId": mainView.currentContainer,
                                              "containerType": containerConfigList.getContainerType(mainView.currentContainer),
                                              "data": command })
        worker.finishedCommand.connect(getPackageVersion)
        worker.start()
    }

    Component.onDestruction: {
        containerConfigList.configChanged.disconnect(reloadStatus)
        worker.finishedCommand.disconnect(getPackageVersion)
        if (install_signal) {
            install_signal.disconnect(installFinished)
        }
    }

    function updateFailureReasonHeight() {
      failureReason.height = Math.max(failureReason.control.height + 10, 48)
    }

    function reloadStatus() {
        statusText = containerConfigList.getAppStatus(currentContainer, currentPackage)

        if (!statusText) {
            statusText = i18n.tr("removed")
        }
    }

    function getPackageVersion(command_output) {
        packageVersionText = containerConfigList.getAppVersion(command_output)
    }

   function installFinished(success, error_msg) {
       if (!success) {
           statusText = i18n.tr("failed")
           failureReasonText = error_msg
           failureReason.visible = true
       }
       install_signal.disconnect(installFinished)
   }
}
