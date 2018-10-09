set(CMAKE_INSTALL_SYSCONFDIR "/etc")

install(FILES libertine-manager-app.desktop
        DESTINATION ${CMAKE_INSTALL_DATADIR}/applications)
install(FILES libertine_64.png libertine-lxc.conf
  DESTINATION ${CMAKE_INSTALL_DATADIR}/${CMAKE_PROJECT_NAME})
install(FILES libertine-xmir.conf replace-libertine-scope.conf
        DESTINATION ${CMAKE_INSTALL_DATADIR}/upstart/sessions)
install(FILES libertine-lxc-sudo libertine-lxd-sudo
        DESTINATION ${CMAKE_INSTALL_SYSCONFDIR}/sudoers.d)

# libertined
install(FILES com.canonical.libertine.Service.service
        DESTINATION ${CMAKE_INSTALL_DATADIR}/dbus-1/services)
pkg_get_variable(SYSTEMD_USER_DIR systemd systemduserunitdir)
install(FILES libertine.service
        DESTINATION ${SYSTEMD_USER_DIR}/)
