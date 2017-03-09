add_test(test_libertine_service dbus-run-session -- /usr/bin/python3 ${CMAKE_CURRENT_SOURCE_DIR}/test_libertine_service.py)
set_tests_properties(test_libertine_service
                     PROPERTIES ENVIRONMENT
                   "PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}:${CMAKE_SOURCE_DIR}/python;LIBERTINE_DATA_DIR=${CMAKE_CURRENT_SOURCE_DIR};PATH=${CMAKE_SOURCE_DIR}/tools:$ENV{PATH};")

add_executable(
  test_liblibertine
  test_liblibertine.cpp
)

target_link_libraries(
  test_liblibertine
  ${LIBERTINE_CORE}
  gtest gtest_main
  ${DBUSTEST_LIBRARIES}
  ${GIO2_LIBRARIES}
  Qt5::Core
)

add_test(test_liblibertine test_liblibertine)

set_tests_properties(test_liblibertine
                     PROPERTIES ENVIRONMENT
                   "PYTHONPATH=${CMAKE_SOURCE_DIR}/python;PATH=${CMAKE_SOURCE_DIR}/tools:$ENV{PATH};XDG_DATA_HOME=${CMAKE_CURRENT_SOURCE_DIR}/data;XDG_CACHE_HOME=${CMAKE_CURRENT_SOURCE_DIR}/data")
