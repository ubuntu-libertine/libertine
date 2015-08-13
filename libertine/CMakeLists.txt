configure_file(config.h.in config.h)

set(API_VERSION 1)
set(ABI_VERSION 1)

add_library(
  liblibertine STATIC
  ContainerManager.cpp
  ContainerConfig.cpp
  ContainerConfigList.cpp
  ContainerAppsList.cpp
  LibertineConfig.cpp
  PasswordHelper.cpp
  libertine_lxc_manager_wrapper.cpp
)
target_link_libraries(liblibertine Qt5::Core python3.4m pam)

add_library(
  libertine-common SHARED
  libertine_common.cpp
  ContainerConfigList.cpp
  LibertineConfig.cpp
  ContainerConfig.cpp
)
set_target_properties(libertine-common PROPERTIES
  VERSION ${ABI_VERSION}.0.0
  SOVERSION ${ABI_VERSION}
  OUTPUT_NAME "libertine"
)
target_link_libraries(libertine-common
  ${GLIB2_LIBRARIES}
  Qt5::Core
)

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
target_link_libraries(libertine liblibertine Qt5::Core Qt5::Quick Qt5::Gui)

add_executable(libertine_container_manager ${libertine_cli_SRC})
target_link_libraries(libertine_container_manager liblibertine Qt5::Core Qt5::Quick Qt5::Gui)

install(DIRECTORY qml DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/${CMAKE_PROJECT_NAME})
install(TARGETS libertine libertine_container_manager RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES libertine_common.h DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/liblibertine-${API_VERSION}")
install(TARGETS  libertine-common LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
