set(pasted_SRC
    pasted.cpp
)

add_executable(pasted ${pasted_SRC})

qt5_use_modules(pasted DBus)

target_link_libraries(pasted Qt5::Core Qt5::Gui Qt5::Widgets content-hub X11)
install(TARGETS pasted RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
