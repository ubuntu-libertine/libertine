add_test(test_libertine_service dbus-run-session -- /usr/bin/python3 ${CMAKE_CURRENT_SOURCE_DIR}/test_libertine_service.py)
set_tests_properties(test_libertine_service
                     PROPERTIES ENVIRONMENT
                   "PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}:${CMAKE_SOURCE_DIR}/python;LIBERTINE_DATA_DIR=${CMAKE_CURRENT_SOURCE_DIR};PATH=${CMAKE_SOURCE_DIR}/tools:$ENV{PATH};")
