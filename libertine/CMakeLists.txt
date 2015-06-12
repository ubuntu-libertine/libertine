find_package(Qt5Gui REQUIRED)
find_package(Qt5Quick REQUIRED)
set(CMAKE_AUTOMOC ON)

configure_file(config.h.in config.h)

file(GLOB_RECURSE QML_SRC *.qml *.js *.json)
set(libertine_SRC 
    ContainerConfig.cpp
    libertine.cpp
    LibertineConfig.cpp
    main.cpp
    libertine_lxc_manager_wrapper.cpp ${QML_SRC})

include_directories(${CMAKE_BINARY_DIR} ${CMAKE_SOURCE_DIR})
add_executable(libertine ${libertine_SRC})
target_link_libraries(libertine Qt5::Quick Qt5::Gui python3.4m)

install(TARGETS libertine RUNTIME DESTINATION bin)
