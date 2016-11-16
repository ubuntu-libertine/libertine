function(create_service_unit_test test_name)
  add_test(${test_name} /usr/bin/python3 -m testtools.run ${test_name})
  set_tests_properties(${test_name}
                       PROPERTIES ENVIRONMENT
                       "GI_TYPELIB_PATH=${CMAKE_BINARY_DIR}/liblibertine;LD_LIBRARY_PATH=${CMAKE_BINARY_DIR}/liblibertine:${LD_LIBRARY_PATH};PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}:${CMAKE_SOURCE_DIR}/python;LIBERTINE_DATA_DIR=${CMAKE_CURRENT_SOURCE_DIR}")
endfunction(create_service_unit_test)

create_service_unit_test(test_container)
create_service_unit_test(test_apt)
create_service_unit_test(test_task_dispatcher)

add_subdirectory(tasks)
