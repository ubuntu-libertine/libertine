set(API_VERSION 1)
set(ABI_VERSION 1)

set(libertine_src ${CMAKE_SOURCE_DIR}/libertine)

add_library(
  libertine-common SHARED
  libertine.cpp
  ${libertine_src}/ContainerConfigList.cpp
  ${libertine_src}/LibertineConfig.cpp
  ${libertine_src}/ContainerConfig.cpp
)
set_target_properties(libertine-common PROPERTIES
  VERSION ${ABI_VERSION}.0.0
  SOVERSION ${ABI_VERSION}
  OUTPUT_NAME "libertine"
)
target_link_libraries(libertine-common
  ${GLIB2_LIBRARIES}
  Qt5::Core
)

install(FILES libertine.h DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/liblibertine-${API_VERSION}")
install(TARGETS libertine-common LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
