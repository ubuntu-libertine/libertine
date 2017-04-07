install(PROGRAMS libertine-container-manager libertine-launch libertine-shell
                 libertine-xmir libertine-lxc-setup libertine-lxd-setup libertined
        DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES libertine-launch.1 libertine-container-manager.1
              libertine-xmir.1 libertine-shell.1
        DESTINATION ${CMAKE_INSTALL_MANDIR}/man1
        COMPONENT doc)
install(FILES completions/libertine-container-manager completions/libertine-shell
        DESTINATION ${DESTDIR}/usr/share/bash-completion/completions/)
