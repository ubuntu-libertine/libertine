execute_process(COMMAND python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"
                OUTPUT_VARIABLE python_site_packages
                OUTPUT_STRIP_TRAILING_WHITESPACE)

install(DIRECTORY libertine
        DESTINATION ${python_site_packages})
