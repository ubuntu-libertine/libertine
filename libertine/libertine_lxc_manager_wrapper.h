/**
 * @file libertine_lxc_manager_wrapper.h
 * @brief Libertine LXC wrapper using the Python module
 */
/*
 * Copyright 2015 Canonical Ltd
 *
 * Libertine is free software: you can redistribute it and/or modify it under
 * the terms of the GNU General Public License, version 3, as published by the
 * Free Software Foundation.
 *
 * Libertine is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
 * A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef LIBERTINE_LXC_MANAGER_WRAPPER_H
#define LIBERTINE_LXC_MANAGER_WRAPPER_H

#include <vector>
#include <python3.4/Python.h>

void initialize_python();

class LibertineManagerWrapper
{
public:
  LibertineManagerWrapper(const char *name);
  ~LibertineManagerWrapper();

  void DestroyLibertineContainer();
  void CreateLibertineContainer(const char *password);
  void CreateLibertineConfig();
  void UpdateLibertineContainer();
  void InstallPackageInContainer(const char *package_name);
  static std::vector<char *> ListLibertineContainers();

private:
  static PyObject* InitializePythonModule();

private:
  PyObject *pInstance_;

  const char* libertine_lxc_name_;
};

#endif
