find_package(Qt5Gui REQUIRED)
find_package(Qt5Quick REQUIRED)
set(CMAKE_AUTOMOC ON)

configure_file(config.h.in config.h)

set(libertine_SRC libertine.cpp main.cpp)

include_directories(${CMAKE_BINARY_DIR} ${CMAKE_SOURCE_DIR})
add_executable(libertine ${libertine_SRC})
target_link_libraries(libertine Qt5::Quick Qt5::Gui)

install(TARGETS libertine RUNTIME DESTINATION bin)
