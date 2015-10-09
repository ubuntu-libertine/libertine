configure_file(config.h.in config.h)

file(GLOB_RECURSE QML_SRC *.qml *.js *.json)
set(libertine_SRC
    libertine.cpp
    main.cpp
    ${QML_SRC}
)

add_executable(libertine ${libertine_SRC})
target_link_libraries(libertine libertine-common Qt5::Core Qt5::Quick Qt5::Gui)

install(DIRECTORY qml DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/${CMAKE_PROJECT_NAME})
install(TARGETS libertine RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
