set(CMAKE_INSTALL_SYSCONFDIR "/etc")

install(FILES libertine-manager-app.desktop
        DESTINATION ${CMAKE_INSTALL_DATADIR}/applications)
install(FILES libertine_64.png libertine-lxc.conf
  DESTINATION ${CMAKE_INSTALL_DATADIR}/${CMAKE_PROJECT_NAME})
install(FILES libertine-xmir.conf
        DESTINATION ${CMAKE_INSTALL_DATADIR}/upstart/sessions)
install(FILES libertine-lxc-sudo
        DESTINATION ${CMAKE_INSTALL_SYSCONFDIR}/sudoers.d)
install(FILES com.canonical.libertine.LxcManager.service
        DESTINATION ${CMAKE_INSTALL_DATADIR}/dbus-1/services)

configure_file("python3-libertine-chroot.click-hook.in"
  "${CMAKE_SOURCE_DIR}/debian/python3-libertine-chroot.click-hook"
  @ONLY)
