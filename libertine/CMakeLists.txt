configure_file(config.h.in config.h)

add_library(
  liblibertine STATIC
  ContainerConfig.cpp
  ContainerConfigList.cpp
  LibertineConfig.cpp
)
target_link_libraries(liblibertine Qt5::Core)

file(GLOB_RECURSE QML_SRC *.qml *.js *.json)
set(libertine_SRC 
    libertine.cpp
    main.cpp
    libertine_lxc_manager_wrapper.cpp
    ${QML_SRC}
)

add_executable(libertine ${libertine_SRC})
target_link_libraries(libertine liblibertine Qt5::Core Qt5::Quick Qt5::Gui python3.4m)

install(TARGETS libertine RUNTIME DESTINATION bin)
