project(libertine CXX)
cmake_minimum_required(VERSION 2.8.9)
set(LIBERTINE_VERSION "0.99")

include(GNUInstallDirs)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall -Wextra -pedantic")

add_subdirectory(libertine)

set(ARCHIVE_NAME ${CMAKE_PROJECT_NAME}-${LIBERTINE_VERSION})
add_custom_target(dist
  COMMAND echo debian export-ignore >.gitattributes
  && git archive --worktree-attributes --prefix=${ARCHIVE_NAME}/ HEAD
     | xz >${CMAKE_BINARY_DIR}/${ARCHIVE_NAME}.tar.xz
  && rm .gitattributes
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

