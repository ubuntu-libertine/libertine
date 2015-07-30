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

const char* LIBERTINE_PYTHON_MODULE = "libertine";
const char* LIBERTINE_CONTAINER_CLASS = "LibertineContainer";

// Methods availaible from the LibertineContainer Python class
const char* PY_DESTROY_LIBERTINE_CONTAINER = "destroy_libertine_container";
const char* PY_CREATE_LIBERTINE_CONTAINER = "create_libertine_container";
const char* PY_CREATE_LIBERTINE_CONFIG = "create_libertine_config";
const char* PY_UPDATE_LIBERTINE_CONTAINER = "update_libertine_container";
const char* PY_INSTALL_PACKAGE_IN_CONTAINER = "install_package";
const char* PY_REMOVE_PACKAGE_IN_CONTAINER = "remove_package";

// Functions outside of the Python class that are needed
const char* PY_LIST_LIBERTINE_CONTAINERS = "list_libertine_containers";

void initialize_python()
{
  Py_Initialize();

  PyEval_InitThreads();
  PyEval_SaveThread();
}


LibertineManagerWrapper::LibertineManagerWrapper(const char *name, const char *type)
: libertine_container_name_(name)
, libertine_container_type_(type)
{
  PyObject *pArgs, *pDict, *pClass;

  PyGILState_STATE gstate;
  gstate = PyGILState_Ensure();

  pDict = InitializePythonModule();

  if (pDict)
  {
    pClass = PyDict_GetItemString(pDict, LIBERTINE_CONTAINER_CLASS);

    if (PyCallable_Check(pClass))
    {
      pArgs = PyTuple_New(2);
      PyTuple_SetItem(pArgs, 0, PyUnicode_FromString(libertine_container_name_));
      PyTuple_SetItem(pArgs, 1, PyUnicode_FromString(libertine_container_type_));
      pInstance_ = PyObject_CallObject(pClass, pArgs);
      Py_DECREF(pArgs);
      Py_DECREF(pClass);
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

  PyGILState_Release(gstate);
}

LibertineManagerWrapper::~LibertineManagerWrapper()
{
}

void LibertineManagerWrapper::DestroyLibertineContainer()
{
  PyGILState_STATE gstate;
  gstate = PyGILState_Ensure();

  PyObject_CallMethod(pInstance_, PY_DESTROY_LIBERTINE_CONTAINER, NULL);

  PyGILState_Release(gstate);
}

void LibertineManagerWrapper::CreateLibertineContainer(const char *password)
{
  PyGILState_STATE gstate;
  gstate = PyGILState_Ensure();

  PyObject_CallMethod(pInstance_, PY_CREATE_LIBERTINE_CONTAINER, "s", password);

  PyGILState_Release(gstate);
}

void LibertineManagerWrapper::CreateLibertineConfig()
{
  PyGILState_STATE gstate;
  gstate = PyGILState_Ensure();

  PyObject_CallMethod(pInstance_, PY_CREATE_LIBERTINE_CONFIG, NULL);

  PyGILState_Release(gstate);
}

void LibertineManagerWrapper::UpdateLibertineContainer()
{
  PyGILState_STATE gstate;
  gstate = PyGILState_Ensure();

  PyObject_CallMethod(pInstance_, PY_UPDATE_LIBERTINE_CONTAINER, NULL);

  PyGILState_Release(gstate);
}

bool LibertineManagerWrapper::InstallPackageInContainer(const char* package_name, char** error_msg)
{
  bool success = true;

  PyGILState_STATE gstate;
  gstate = PyGILState_Ensure();

  PyObject *result = PyObject_CallMethod(pInstance_, PY_INSTALL_PACKAGE_IN_CONTAINER, "s", package_name);

  if (result)
  {
    if (PyTuple_GetItem(result, 0) == Py_False)
    {
      PyObject *msg;
      if (PyUnicode_Check((msg = PyTuple_GetItem(result, 1))))
      {
        strncpy(*error_msg, PyUnicode_AsUTF8(msg), 1024);
        success = false;
      }
    }
    Py_DECREF(result);
  }
  else
  {
    PyErr_Print();
  }

  PyGILState_Release(gstate);

  return success;
}

bool LibertineManagerWrapper::RemovePackageInContainer(const char* package_name, char** error_msg)
{
  bool success = true;

  PyGILState_STATE gstate;
  gstate = PyGILState_Ensure();

  PyObject *result = PyObject_CallMethod(pInstance_, PY_REMOVE_PACKAGE_IN_CONTAINER, "s", package_name);

  if (result)
  {
    if (PyTuple_GetItem(result, 0) == Py_False)
    {
      PyObject *msg;
      if (PyUnicode_Check((msg = PyTuple_GetItem(result, 1))))
      {
        strncpy(*error_msg, PyUnicode_AsUTF8(msg), 1024);
        success = false;
      }
    }
    Py_DECREF(result);
  }
  else
  {
    PyErr_Print();
  }

  PyGILState_Release(gstate);

  return success;
}

std::vector<char *>LibertineManagerWrapper::ListLibertineContainers()
{
  PyObject *pDict, *pFunc, *pValue;
  std::vector<char *>existing_libertine_containers;

  pDict = InitializePythonModule();

  if (pDict)
  {
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
  }

  return existing_libertine_containers;
}

PyObject* LibertineManagerWrapper::InitializePythonModule()
{
  PyObject *pName, *pModule, *pDict = NULL;

  /* for running from the source root directory */
  PyRun_SimpleString("import sys; sys.path.append('python')\n");

  pName = PyUnicode_FromString(LIBERTINE_PYTHON_MODULE);

  pModule = PyImport_Import(pName);
  Py_DECREF(pName);

  if (pModule != NULL)
  {
    pDict = PyModule_GetDict(pModule);
    Py_DECREF(pModule);
  }

  return pDict;
}

