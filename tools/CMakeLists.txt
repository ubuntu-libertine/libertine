install(PROGRAMS libertine-container-manager libertine-launch libertine-session-bridge libertine-lxc-manager libertine-xmir
        DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES libertine-launch.1 libertine-container-manager.1 libertine-session-bridge.1 libertine-lxc-manager.1 libertine-xmir.1
        DESTINATION ${CMAKE_INSTALL_MANDIR}/man1
        COMPONENT doc)
