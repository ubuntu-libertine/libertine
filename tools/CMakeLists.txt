install(PROGRAMS libertine-container-manager libertine-launch libertine-lxc-manager libertine-xmir libertine-lxc-setup libertined
        DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES libertine-launch.1 libertine-container-manager.1 libertine-lxc-manager.1 libertine-xmir.1
        DESTINATION ${CMAKE_INSTALL_MANDIR}/man1
        COMPONENT doc)
install(PROGRAMS update-puritine-containers
        DESTINATION ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}/libertine)

install(FILES completions/libertine-container-manager
        DESTINATION ${DESTDIR}/usr/share/bash-completion/completions/)
