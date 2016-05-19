install(FILES libertine.desktop
        DESTINATION ${CMAKE_INSTALL_DATADIR}/applications)
install(FILES libertine_64.png libertine-lxc.conf
  DESTINATION ${CMAKE_INSTALL_DATADIR}/${CMAKE_PROJECT_NAME})
install(FILES libertine-lxc-manager.conf libertine-xmir.conf
        DESTINATION ${CMAKE_INSTALL_DATADIR}/upstart/sessions)
install(FILES puritine-15.04.1.framework
        DESTINATION ${CMAKE_INSTALL_DATADIR}/click/frameworks)

configure_file("libertine-tools.click-hook.in"
  "${CMAKE_SOURCE_DIR}/debian/libertine-tools.click-hook"
  @ONLY)
