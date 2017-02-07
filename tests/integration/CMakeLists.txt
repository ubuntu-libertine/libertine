add_test(test_libertine_service dbus-run-session /usr/bin/python3 -m testtools.run test_libertine_service)
set_tests_properties(test_libertine_service
                     PROPERTIES ENVIRONMENT
                   "GI_TYPELIB_PATH=${CMAKE_BINARY_DIR}/liblibertine;LD_LIBRARY_PATH=${CMAKE_BINARY_DIR}/liblibertine:${LD_LIBRARY_PATH};PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}:${CMAKE_SOURCE_DIR}/python;LIBERTINE_DATA_DIR=${CMAKE_CURRENT_SOURCE_DIR};PATH=${CMAKE_SOURCE_DIR}/tools:$ENV{PATH};")
