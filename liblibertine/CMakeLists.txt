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
