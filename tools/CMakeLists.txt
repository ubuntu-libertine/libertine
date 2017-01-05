install(PROGRAMS libertine-container-manager libertine-launch libertine-lxc-manager libertine-lxd-manager
                 libertine-xmir libertine-lxc-setup libertine-lxd-setup libertined
        DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES libertine-launch.1 libertine-container-manager.1 libertine-lxc-manager.1
              libertine-lxd-manager.1 libertine-xmir.1
        DESTINATION ${CMAKE_INSTALL_MANDIR}/man1
        COMPONENT doc)
install(FILES completions/libertine-container-manager
        DESTINATION ${DESTDIR}/usr/share/bash-completion/completions/)
