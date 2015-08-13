set(GTEST_ROOT /usr/src/gtest)
add_subdirectory(${GTEST_ROOT} ${CMAKE_CURRENT_BINARY_DIR}/gtest)

add_definitions ( -DCMAKE_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}" )

add_executable(
  test_container_config
  ContainerConfigTests.cpp
  ContainerConfigListTests.cpp
)
target_link_libraries(
  test_container_config
  liblibertine
  gtest gtest_main
  Qt5::Core
)

add_test(test_container_config
  test_container_config
)

add_executable(
  test_libertine_common
  LibertineCommonTests.cpp
)
target_link_libraries(
  test_libertine_common
  libertine-common
  gtest gtest_main
)

add_test(test_libertine_common
  test_libertine_common
)
