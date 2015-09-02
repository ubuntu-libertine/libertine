execute_process(COMMAND dpkg-architecture -qDEB_BUILD_ARCH
        OUTPUT_VARIABLE BUILD_ARCH
        OUTPUT_STRIP_TRAILING_WHITESPACE
)

configure_file("trusty_firefox_0.0.desktop.in" "${CMAKE_CURRENT_BINARY_DIR}/trusty_firefox_0.0.desktop" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/trusty_firefox_0.0.desktop"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/applications/demo")

configure_file("trusty_gedit_0.0.desktop.in" "${CMAKE_CURRENT_BINARY_DIR}/trusty_gedit_0.0.desktop" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/trusty_gedit_0.0.desktop"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/applications/demo")

configure_file("trusty_gimp_0.0.desktop.in" "${CMAKE_CURRENT_BINARY_DIR}/trusty_gimp_0.0.desktop" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/trusty_gimp_0.0.desktop"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/applications/demo")

configure_file("trusty_libreoffice-startcenter_0.0.desktop.in" "${CMAKE_CURRENT_BINARY_DIR}/trusty_libreoffice-startcenter_0.0.desktop" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/trusty_libreoffice-startcenter_0.0.desktop"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/applications/demo")

configure_file("trusty_xchat-gnome_0.0.desktop.in" "${CMAKE_CURRENT_BINARY_DIR}/trusty_xchat-gnome_0.0.desktop" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/trusty_xchat-gnome_0.0.desktop"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/applications/demo")
