cmake_minimum_required(VERSION 3.0.2)
cmake_policy(SET CMP0048 NEW)

project(libertine 
        VERSION 0.99.1
        LANGUAGES CXX)

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

