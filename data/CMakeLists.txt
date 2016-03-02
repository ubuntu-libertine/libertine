add_subdirectory(demo)

install(FILES libertine.desktop
        DESTINATION ${CMAKE_INSTALL_DATADIR}/applications)
install(FILES libertine_64.png libertine-lxc.conf
  DESTINATION ${CMAKE_INSTALL_DATADIR}/${CMAKE_PROJECT_NAME})
install(FILES puritine-click.conf libertine-lxc-manager.conf libertine-xmir.conf
        DESTINATION ${CMAKE_INSTALL_DATADIR}/upstart/sessions)
install(FILES puritine-15.04.1.framework
        DESTINATION ${CMAKE_INSTALL_DATADIR}/click/frameworks)
