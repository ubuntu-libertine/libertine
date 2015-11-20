install(PROGRAMS libertine-container-manager libertine-launch libertine-session-bridge DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES libertine-launch.1
        DESTINATION ${CMAKE_INSTALL_MANDIR}/man1
        COMPONENT doc)
