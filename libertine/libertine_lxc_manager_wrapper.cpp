/**
 * @file libertine_lxc_manager_wrapper.cpp
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

#include <cstdlib>
#include "libertine_lxc_manager_wrapper.h"

const char* LIBERTINE_PYTHON_MODULE = "LibertineContainerTools";
const char* LIBERTINE_CONTAINER_CLASS = "LibertineContainer";

// Methods availaible from the LibertineContainer Python class
const char* PY_DESTROY_LIBERTINE_CONTAINER = "destroy_libertine_container";
const char* PY_CREATE_LIBERTINE_CONTAINER = "create_libertine_container";
const char* PY_CREATE_LIBERTINE_CONFIG = "create_libertine_config";
const char* PY_UPDATE_LIBERTINE_CONTAINER = "update_libertine_container";
const char* PY_INSTALL_PACKAGE_IN_CONTAINER = "install_package";

// Functions outside of the Python class that are needed
const char* PY_LIST_LIBERTINE_CONTAINERS = "list_libertine_containers";

LibertineManagerWrapper::LibertineManagerWrapper(const char *name)
: libertine_lxc_name_(name)
{
  Py_Initialize();

  pName_ = PyUnicode_FromString(LIBERTINE_PYTHON_MODULE);

  pModule_ = PyImport_Import(pName_);
  Py_DECREF(pName_);

  if (pModule_ != NULL)
  {
    pDict_ = PyModule_GetDict(pModule_);

    pClass_ = PyDict_GetItemString(pDict_, LIBERTINE_CONTAINER_CLASS);

    if (PyCallable_Check(pClass_))
    {
      pArgs_ = PyTuple_New(1);
      PyTuple_SetItem(pArgs_, 0, PyUnicode_FromString(libertine_lxc_name_));
      pInstance_ = PyObject_CallObject(pClass_, pArgs_);
      Py_DECREF(pClass_);
    }
    else
    {
      PyErr_Print();
    }
  }
  else
  {
    PyErr_Print();
  }
}

LibertineManagerWrapper::~LibertineManagerWrapper()
{
  Py_DECREF(pInstance_);

  Py_Finalize();
}

void LibertineManagerWrapper::DestroyLibertineContainer()
{
  PyObject_CallMethod(pInstance_, PY_DESTROY_LIBERTINE_CONTAINER, NULL);
}

void LibertineManagerWrapper::CreateLibertineContainer()
{
  PyObject_CallMethod(pInstance_, PY_CREATE_LIBERTINE_CONTAINER, NULL);
}

void LibertineManagerWrapper::CreateLibertineConfig()
{
  PyObject_CallMethod(pInstance_, PY_CREATE_LIBERTINE_CONFIG, NULL);
}

void LibertineManagerWrapper::UpdateLibertineContainer()
{
  PyObject_CallMethod(pInstance_, PY_UPDATE_LIBERTINE_CONTAINER, NULL);
}

void LibertineManagerWrapper::InstallPackageInContainer(const char* package_name)
{
  PyObject_CallMethod(pInstance_, PY_INSTALL_PACKAGE_IN_CONTAINER, "s", package_name);
}

std::vector<char *>LibertineManagerWrapper::ListLibertineContainers()
{
  PyObject *pName, *pModule, *pDict, *pFunc, *pValue;
  std::vector<char *>existing_libertine_containers;

  Py_Initialize();

  pName = PyUnicode_FromString(LIBERTINE_PYTHON_MODULE);

  pModule = PyImport_Import(pName);
  Py_DECREF(pName);

  if (pModule != NULL)
  {
    pDict = PyModule_GetDict(pModule);

    pFunc = PyDict_GetItemString(pDict, PY_LIST_LIBERTINE_CONTAINERS);

    if (PyCallable_Check(pFunc))
    {
      pValue = PyObject_CallObject(pFunc, NULL);

      if (pValue != NULL)
      {
        if (PyTuple_Check(pValue))
        {
          PyObject* pStr;
          char* str;
          for (int i = 0; i < PyTuple_Size(pValue); ++i)
          {
            pStr = PyUnicode_AsEncodedString(PyTuple_GetItem(pValue, i), "utf-8", "Error ~");
            str =  PyBytes_AS_STRING(pStr);
            existing_libertine_containers.push_back(str);
          }
        }
        Py_DECREF(pValue);
      }
    }
    Py_DECREF(pModule);
  }

  Py_Finalize();

  return existing_libertine_containers;
}

