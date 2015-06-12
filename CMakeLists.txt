cmake_minimum_required(VERSION 3.0.2)
cmake_policy(SET CMP0048 NEW)

project(libertine 
        VERSION 0.99.1
        LANGUAGES CXX)

include(GNUInstallDirs)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall -Wextra -pedantic")

include_directories(${CMAKE_BINARY_DIR} ${CMAKE_SOURCE_DIR})

find_package(Qt5Core  REQUIRED)
find_package(Qt5Gui   REQUIRED)
find_package(Qt5Quick REQUIRED)
set(CMAKE_AUTOMOC ON)

add_subdirectory(libertine)

include(CTest)
add_subdirectory(tests)

set(ARCHIVE_NAME ${CMAKE_PROJECT_NAME}-${LIBERTINE_VERSION})
add_custom_target(dist
  COMMAND echo debian export-ignore >.gitattributes
  && git archive --worktree-attributes --prefix=${ARCHIVE_NAME}/ HEAD
     | xz >${CMAKE_BINARY_DIR}/${ARCHIVE_NAME}.tar.xz
  && rm .gitattributes
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

