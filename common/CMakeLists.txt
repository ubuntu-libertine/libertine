add_library(${LIBERTINE_COMMON}
    ContainerAppsList.cpp
    ContainerArchivesList.cpp
    ContainerConfig.cpp
    ContainerConfigList.cpp
    ContainerManager.cpp
    LibertineConfig.cpp
    PackageOperationDetails.cpp
)

target_link_libraries(${LIBERTINE_COMMON} ${LIBERTINE_CORE} Qt5::Core)

install(TARGETS ${LIBERTINE_COMMON_NAME} LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
