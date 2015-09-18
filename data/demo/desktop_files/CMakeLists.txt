execute_process(COMMAND dpkg-architecture -qDEB_BUILD_ARCH
        OUTPUT_VARIABLE BUILD_ARCH
        OUTPUT_STRIP_TRAILING_WHITESPACE
)

configure_file("puritine_firefox_0.0.desktop.in" "${CMAKE_CURRENT_BINARY_DIR}/puritine_firefox_0.0.desktop" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/puritine_firefox_0.0.desktop"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/applications/demo")

configure_file("puritine_gedit_0.0.desktop.in" "${CMAKE_CURRENT_BINARY_DIR}/puritine_gedit_0.0.desktop" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/puritine_gedit_0.0.desktop"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/applications/demo")

configure_file("puritine_gimp_0.0.desktop.in" "${CMAKE_CURRENT_BINARY_DIR}/puritine_gimp_0.0.desktop" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/puritine_gimp_0.0.desktop"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/applications/demo")

configure_file("puritine_libreoffice-startcenter_0.0.desktop.in" "${CMAKE_CURRENT_BINARY_DIR}/puritine_libreoffice-startcenter_0.0.desktop" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/puritine_libreoffice-startcenter_0.0.desktop"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/applications/demo")

configure_file("puritine_xchat-gnome_0.0.desktop.in" "${CMAKE_CURRENT_BINARY_DIR}/puritine_xchat-gnome_0.0.desktop" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/puritine_xchat-gnome_0.0.desktop"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/applications/demo")
