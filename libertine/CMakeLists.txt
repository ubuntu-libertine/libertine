find_package(Qt5Gui)

configure_file(config.h.in config.h)

set(libertine_SRC main.cpp)

include_directories(${CMAKE_BINARY_DIR})
add_executable(libertine ${libertine_SRC})
target_link_libraries(libertine Qt5::Gui)

install(TARGETS libertine RUNTIME DESTINATION bin)
