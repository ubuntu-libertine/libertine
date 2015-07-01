configure_file(config.h.in config.h)

add_library(
  liblibertine STATIC
  ContainerManager.cpp
  ContainerConfig.cpp
  ContainerConfigList.cpp
  LibertineConfig.cpp
  PasswordHelper.cpp
  libertine_lxc_manager_wrapper.cpp
)
target_link_libraries(liblibertine Qt5::Core python3.4m pam)

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

install(TARGETS libertine RUNTIME DESTINATION bin)
