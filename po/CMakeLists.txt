set (GETTEXT_PACKAGE "libertine")

intltool_update_potfile(
  ALL
  UBUNTU_SDK_DEFAULTS
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
