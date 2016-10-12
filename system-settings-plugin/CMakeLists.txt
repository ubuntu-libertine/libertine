set(PLUGIN_MANIFEST_DIR_BASE share/ubuntu/settings/system)
set(PLUGIN_MODULE_DIR_BASE ubuntu-system-settings)

set(PLUGIN_MANIFEST_DIR "${CMAKE_INSTALL_PREFIX}/${PLUGIN_MANIFEST_DIR_BASE}")
set(PLUGIN_MODULE_DIR "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}/${PLUGIN_MODULE_DIR_BASE}")
set(PLUGIN_QML_DIR "${CMAKE_INSTALL_PREFIX}/share/ubuntu/settings/system/qml-plugins/libertine")

SET(CMAKE_INSTALL_RPATH "${PLUGIN_MODULE_DIR}")

configure_file(config.h.in config.h)

set(LIBERTINE_PLUGIN_ICON_PATH "${PLUGIN_MANIFEST_DIR}/icons")
set(PLUGIN_SETTINGS_TARGET libertine.settings)
configure_file(${PLUGIN_SETTINGS_TARGET}.in ${PLUGIN_SETTINGS_TARGET})

set (CMAKE_INCLUDE_CURRENT_DIR ON)
set (CMAKE_AUTOMOC ON)

# For some reason, building on vivid seems to require that we manually
# add /usr/include to the include directories when using automoc here.
set (CMAKE_AUTOMOC_MOC_OPTIONS -I/usr/include)

pkg_check_modules(SYSTEM_SETTINGS REQUIRED SystemSettings)

file(GLOB_RECURSE PLUGIN_QML_SRC
     ${CMAKE_SOURCE_DIR}/qml/common/*.qml
     ${CMAKE_SOURCE_DIR}/qml/plugin/*.qml
)

add_library(libertine-plugin MODULE plugin.cpp plugin.h ${PLUGIN_QML_SRC})
qt5_use_modules(libertine-plugin Qml Quick)

include_directories(${SYSTEM_SETTINGS_INCLUDE_DIRS} ${CMAKE_SOURCE_DIR}/libertine)
target_link_libraries(libertine-plugin ${LIBERTINE_COMMON} ${SYSTEM_SETTINGS_LIBRARIES})

install(TARGETS libertine-plugin LIBRARY DESTINATION ${PLUGIN_MODULE_DIR} NAMELINK_SKIP)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/${PLUGIN_SETTINGS_TARGET} DESTINATION ${PLUGIN_MANIFEST_DIR})
install(FILES libertine-plugin.png DESTINATION ${LIBERTINE_PLUGIN_ICON_PATH})
