# Customize this function from cmake-extras to handle additional options for
# parsing python files and our python command line tools (LP: #1675865)
macro(_WRITE_INTLTOOL_MAKEFILE_IN ARG_PO_DIRECTORY ARG_KEYWORDS
                                  ARG_COPYRIGHT_HOLDER)
    set(_KEYWORDS "XGETTEXT_KEYWORDS=-Lc -Lc++ -Lpython")
    if(NOT "${ARG_COPYRIGHT_HOLDER}" STREQUAL "")
        set(_KEYWORDS "${_KEYWORDS} --copyright-holder='${ARG_COPYRIGHT_HOLDER}'")
    endif()
    foreach(_KEYWORD ${${ARG_KEYWORDS}})
        set(_KEYWORDS "${_KEYWORDS} --keyword=${_KEYWORD}")
    endforeach()
    file(WRITE "${ARG_PO_DIRECTORY}/Makefile.in.in" "${_KEYWORDS}\n")
endmacro()

# Customize this function from cmake-extras to handle additional options for
# parsing python files and our python command line tools (LP: #1675864)
function(_INTLTOOL_LIST_FILTER INPUT OUTPUT)
    set(_multiValueArgs EXPRESSIONS)
    cmake_parse_arguments(_ARG "" "" "${_multiValueArgs}" ${ARGN})

    if(_ARG_EXPRESSIONS)
        set(_TMP "")
        foreach(_ITEM ${${INPUT}})
            unset(_MATCHED)
            foreach(_REGEX ${_ARG_EXPRESSIONS})
                if("${_ITEM}" MATCHES "${_REGEX}")
                  set(_MATCHED ON)
                  break()
                endif()
            endforeach()
            if(NOT _MATCHED)
              list(APPEND _TMP "${_ITEM}")
            endif()
        endforeach()
        set(${OUTPUT} "${_TMP}" PARENT_SCOPE)
        unset(_TMP)
    else()
        set(${OUTPUT} "${${INPUT}}" PARENT_SCOPE)
    endif()
endfunction()

set (GETTEXT_PACKAGE "libertine")

intltool_update_potfile(
  UBUNTU_SDK_DEFAULTS
  FILE_GLOBS "${CMAKE_SOURCE_DIR}/python/libertine/**/*.py;${CMAKE_SOURCE_DIR}/tools/libertine-*"
  FILTER "__init__.py;.bzr/*;parts/*;stage/*;prime/*"
  POTFILES_TEMPLATE POTFILES.in.in
  COPYRIGHT_HOLDER "Canonical Ltd."
  GETTEXT_PACKAGE ${GETTEXT_PACKAGE}
)

intltool_install_translations(
  ALL
  GETTEXT_PACKAGE ${GETTEXT_PACKAGE}
)

file(GLOB_RECURSE ALL_POFILES "*.po")

add_custom_target(potfiles
  ALL
  SOURCES
    POTFILES.in.in
    ${GETTEXT_PACKAGE}.pot
    ${ALL_POFILES}
)
