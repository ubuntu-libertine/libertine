set(CMAKE_INSTALL_SYSCONFDIR "/etc")

install(FILES libertine.desktop
        DESTINATION ${CMAKE_INSTALL_DATADIR}/applications)
install(FILES libertine_64.png libertine-lxc.conf
  DESTINATION ${CMAKE_INSTALL_DATADIR}/${CMAKE_PROJECT_NAME})
install(FILES libertine-lxc-manager.conf libertine-xmir.conf
        DESTINATION ${CMAKE_INSTALL_DATADIR}/upstart/sessions)
install(FILES libertine-lxc-sudo
        DESTINATION ${CMAKE_INSTALL_SYSCONFDIR}/sudoers.d)

configure_file("python3-libertine-chroot.click-hook.in"
  "${CMAKE_SOURCE_DIR}/debian/python3-libertine-chroot.click-hook"
  @ONLY)
