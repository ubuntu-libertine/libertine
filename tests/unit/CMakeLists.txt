set(GTEST_ROOT /usr/src/gtest)
add_subdirectory(${GTEST_ROOT} ${CMAKE_CURRENT_BINARY_DIR}/gtest)

add_definitions ( -DCMAKE_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}" )

add_executable(
  test_container_config
  ContainerConfigListTests.cpp
  ContainersConfigTests.cpp
)

target_link_libraries(
  test_container_config
  ${LIBERTINE_COMMON}
  gtest gtest_main
  Qt5::Core
)

add_test(test_container_config
  test_container_config
)

add_test(test_libertine "py.test-3" "${CMAKE_CURRENT_SOURCE_DIR}" "-v" "--junit-xml=test_libertine.xml" "--ignore=${CMAKE_CURRENT_SOURCE_DIR}/test_launcher_with_dbus.py")
set_tests_properties(test_libertine
                     PROPERTIES ENVIRONMENT
                     "GI_TYPELIB_PATH=${CMAKE_BINARY_DIR}/liblibertine;LD_LIBRARY_PATH=${CMAKE_BINARY_DIR}/liblibertine:${LD_LIBRARY_PATH};CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR};PYTHONPATH=${CMAKE_SOURCE_DIR}/python;CMAKE_SOURCE_DIR=${CMAKE_SOURCE_DIR};LIBERTINE_DATA_DIR=${CMAKE_CURRENT_SOURCE_DIR}")

add_test(test_libertine_with_dbus "py.test-3" "${CMAKE_CURRENT_SOURCE_DIR}/test_launcher_with_dbus.py" "-v" "--junit-xml=test_libertine_with_dbus.xml" )
set_tests_properties(test_libertine_with_dbus
                     PROPERTIES
                     ENVIRONMENT
                     "GI_TYPELIB_PATH=${CMAKE_BINARY_DIR}/liblibertine;LD_LIBRARY_PATH=${CMAKE_BINARY_DIR}/liblibertine:${LD_LIBRARY_PATH};CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR};PYTHONPATH=${CMAKE_SOURCE_DIR}/python;CMAKE_SOURCE_DIR=${CMAKE_SOURCE_DIR}")

add_subdirectory(service)
