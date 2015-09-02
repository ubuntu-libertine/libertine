add_subdirectory(desktop_files)

install(DIRECTORY icons/
        DESTINATION ${CMAKE_INSTALL_DATADIR}/${CMAKE_PROJECT_NAME}/demo/icons)
