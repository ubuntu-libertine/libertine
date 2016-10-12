configure_file(config.h.in config.h)

file(GLOB_RECURSE QML_SRC
  ${CMAKE_SOURCE_DIR}/qml/common/*.qml
  ${CMAKE_SOURCE_DIR}/qml/gui/*.qml
)
set(libertine_SRC
    libertine.cpp
    main.cpp

    ${QML_SRC} # so the QML files show up in Qt Creator
)

add_executable(${LIBERTINE_EXE_NAME} ${libertine_SRC})
target_link_libraries(${LIBERTINE_EXE_NAME} ${LIBERTINE_COMMON} ${LIBERTINE_CORE} Qt5::Core Qt5::Quick Qt5::Gui)

install(DIRECTORY qml DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/${CMAKE_PROJECT_NAME})

install(TARGETS ${LIBERTINE_EXE_NAME} RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
