set(API_VERSION 1)
set(ABI_VERSION 1)

set(libertine_src ${CMAKE_SOURCE_DIR}/libertine)

add_library(
  libertine-common SHARED
  libertine.cpp
  ${libertine_src}/ContainerConfigList.cpp
  ${libertine_src}/LibertineConfig.cpp
  ${libertine_src}/ContainerConfig.cpp
  ${libertine_src}/ContainerManager.cpp
  ${libertine_src}/ContainerAppsList.cpp
  ${libertine_src}/PasswordHelper.cpp
  ${libertine_src}/libertine_lxc_manager_wrapper.cpp
)
set_target_properties(libertine-common PROPERTIES
  VERSION ${ABI_VERSION}.0.0
  SOVERSION ${ABI_VERSION}
  OUTPUT_NAME "libertine"
)
target_link_libraries(libertine-common
  ${GLIB2_LIBRARIES}
  ${PYTHON3_LIBRARIES}
  Qt5::Core
  pam
)

install(FILES libertine.h DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/liblibertine-${API_VERSION}")
install(TARGETS libertine-common LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})

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
