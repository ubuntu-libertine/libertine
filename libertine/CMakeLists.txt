
configure_file(config.h.in config.h)

set(libertine_SRC main.cpp)

include_directories(${CMAKE_BINARY_DIR})
add_executable(libertine ${libertine_SRC})

install(TARGETS libertine RUNTIME DESTINATION bin)
