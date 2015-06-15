set(GTEST_ROOT /usr/src/gtest)
add_subdirectory(${GTEST_ROOT} ${CMAKE_CURRENT_BINARY_DIR}/gtest)

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
