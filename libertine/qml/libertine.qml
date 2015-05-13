import QtQuick 2.0
import Ubuntu.Components 0.1

MainView {
    id: mainview
    objectName: "mainView"
    applicationName: "Legacy Application Manager"
    useDeprecatedToolbar: false
    width: units.gu(60)
    height: units.gu(75)
    property real margins: units.gu(2)

    Page {
        id: placeholder
        title: "Placeholder Page"
    }
}
