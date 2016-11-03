set(API_VERSION 1)
set(ABI_VERSION 1)

set(COMMON_DIR ${CMAKE_SOURCE_DIR}/common)

add_library(
  ${LIBERTINE_CORE} SHARED
  libertine.cpp

  ${COMMON_DIR}/ContainerConfig.cpp
  ${COMMON_DIR}/ContainerConfigList.cpp
  ${COMMON_DIR}/LibertineConfig.cpp
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
)

# "liblibertine_headers_path" is used in libertine.pc.in
set(liblibertine_headers_path "${CMAKE_INSTALL_FULL_INCLUDEDIR}/liblibertine")
install(FILES libertine.h DESTINATION ${liblibertine_headers_path})
install(TARGETS ${LIBERTINE_CORE} LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})

configure_file(libertine.pc.in ${CMAKE_BINARY_DIR}/libertine.pc @ONLY)
install(FILES ${CMAKE_BINARY_DIR}/libertine.pc
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig)

##########################
# Introspection
##########################

include(UseGObjectIntrospection)

set(INTROSPECTION_GIRS)
set(_introspection_files libertine.h)
set(Libertine_1_gir "libertine")
set(Libertine_1_gir_INCLUDES GObject-2.0)

gir_get_cflags(_cflags)
set(Libertine_1_gir_CFLAGS ${c_flags})
set(Libertine_1_gir_LIBS libertine)

list_make_absolute(_abs_introspection_files _introspection_files "${CMAKE_CURRENT_SOURCE_DIR}/")
set(Libertine_1_gir_FILES ${_abs_introspection_files})
set(Libertine_1_gir_SCANNERFLAGS --c-include "libertine.h")
set(Libertine_1_gir_EXPORT_PACKAGES "libertine-${API_VERSION}")

list(APPEND INTROSPECTION_GIRS Libertine-1.gir)
gir_add_introspections(INTROSPECTION_GIRS)

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/Libertine-1.typelib" DESTINATION "${CMAKE_INSTALL_LIBDIR}/girepository-1.0")
