set(API_VERSION 1)
set(ABI_VERSION 1)

add_library(
  ${LIBERTINE_CORE} SHARED
  libertine.cpp

  # libertined client
  libertined.cpp
)

set_target_properties(${LIBERTINE_CORE} PROPERTIES
  VERSION ${ABI_VERSION}.0.0
  SOVERSION ${ABI_VERSION}
  OUTPUT_NAME "libertine"
)

target_link_libraries(${LIBERTINE_CORE}
  ${GLIB2_LIBRARIES}
  ${PYTHON3_LIBRARIES}
  Qt5::Core
  Qt5::DBus
)

# "liblibertine_headers_path" is used in libertine.pc.in
set(liblibertine_headers_path "${CMAKE_INSTALL_FULL_INCLUDEDIR}/liblibertine")
install(FILES libertine.h DESTINATION ${liblibertine_headers_path})
install(TARGETS ${LIBERTINE_CORE} LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})

configure_file(libertine.pc.in ${CMAKE_BINARY_DIR}/libertine.pc @ONLY)
install(FILES ${CMAKE_BINARY_DIR}/libertine.pc
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig)
