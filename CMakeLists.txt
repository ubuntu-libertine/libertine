project(com.ubuntu.libertine CXX)
cmake_minimum_required(VERSION 2.8.9)
set(LIBERTINE_VERSION "1.0.0")

include(GNUInstallDirs)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall -Wextra -pedantic")

add_subdirectory(libertine)

