install(PROGRAMS libertine-container-manager libertine-launch libertine-session-bridge libertine-lxc-manager libertine-xmir
        DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES libertine-launch.1 libertine-container-manager.1 libertine-session-bridge.1 libertine-lxc-manager.1 libertine-xmir.1
        DESTINATION ${CMAKE_INSTALL_MANDIR}/man1
        COMPONENT doc)
install(PROGRAMS update-puritine-containers
        DESTINATION ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}/libertine)

install(FILES bash_completion.d/libertine-container-manager
        DESTINATION ${DESTDIR}/etc/bash_completion.d)
