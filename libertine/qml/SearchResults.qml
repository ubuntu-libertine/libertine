import QtQuick 2.4
import QtQuick.Layouts 1.0
import Ubuntu.Components 1.2


UbuntuListView {
    id: listView
    anchors.fill: parent
    
    delegate: ListItem {
        id: packageItem
        Label {
            text: model.package_desc
        }
        trailingActions: ListItemActions {
            actions: [
                Action {
                    iconName: "select"
                    description: i18n.tr("Install Package")
                    onTriggered: {
                         if (!containerConfigList.isAppInstalled(mainView.currentContainer, model.package_name)) {
                             containerAppsList.addNewApp(mainView.currentContainer, model.package_name)
                             installPackage(model.package_name)
                         }
                    }
                }
            ]
        }
    }
}
