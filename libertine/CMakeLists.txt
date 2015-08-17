configure_file(config.h.in config.h)

file(GLOB_RECURSE QML_SRC *.qml *.js *.json)
set(libertine_SRC
    libertine.cpp
    main.cpp
    ${QML_SRC}
)
set(libertine_cli_SRC
    libertine_container_manager_cli.cpp
)

add_executable(libertine ${libertine_SRC})
target_link_libraries(libertine libertine-common Qt5::Core Qt5::Quick Qt5::Gui)

add_executable(libertine_container_manager ${libertine_cli_SRC})
target_link_libraries(libertine_container_manager libertine-common Qt5::Core Qt5::Quick)

install(DIRECTORY qml DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/${CMAKE_PROJECT_NAME})
install(TARGETS libertine libertine_container_manager RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
