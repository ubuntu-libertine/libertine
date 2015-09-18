add_subdirectory(demo)

install(FILES libertine.desktop
        DESTINATION ${CMAKE_INSTALL_DATADIR}/applications)
install(FILES libertine_64.png
  DESTINATION ${CMAKE_INSTALL_DATADIR}/${CMAKE_PROJECT_NAME})
install(FILES puritine-click.conf
        DESTINATION ${CMAKE_INSTALL_DATADIR}/upstart/sessions)
