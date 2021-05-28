#!/usr/bin/env python
"""
    Utility class used to load in plugin modules for strategies or injectors.
    Copyright (C) 2021  Bradford G. Van Treuren

    Utility class used to load in plugin modules for strategies or injectors.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

__authors__ = ["Bradford G. Van Treuren"]
__contact__ = "bradvt59@gmail.com"
__copyright__ = "Copyright 2021, VT Enterprises Consulting Services"
__credits__ = ["Bradford G. Van Treuren"]
__date__ = "2021/02/12"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


import importlib
import importlib.util
import inspect
import sys
from enum import Enum
import os
import platform

from p2654model2.builder.moduleinfo import ModuleInfo, ClassInfo, FunctionInfo


class ModuleType(Enum):
    UNDEFINED = 0
    BUILTIN = 1
    EXTERNAL = 2


class ModuleLoader(object):
    inst = None

    @staticmethod
    def get_moduleloader():
        if ModuleLoader.inst is None:
            ModuleLoader.inst = ModuleLoader()
        return ModuleLoader.inst

    def __init__(self):
        self.__module_name = None
        self.__module_type = ModuleType.UNDEFINED
        self.__search_path_list = []
        self.__module = None
        self.__module_info_list = []

    def get_module_info_list(self):
        return self.__module_info_list

    def get_module_info(self, mod):
        for m in self.__module_info_list:
            if m.name == mod:
                return m
        return None

    def add_search_path_list(self, searchpath):
        if searchpath not in self.__search_path_list:
            self.__search_path_list.append(searchpath)

    def add_sys_path(self, spath):
        if spath not in sys.path:
            sys.path.append(spath)

    def get_search_path_list(self):
        return self.__search_path_list

    def load(self, module_name, class_name):
        # print("module_name = ", module_name)
        self.__module_name = module_name
        for m in self.__module_info_list:
            if m.name == module_name:
                for c in m.get_classes():
                    if c.name == class_name:
                        return m.obj
            if os.path.basename(m.obj.__dict__["__file__"]).split('.')[0] == class_name:
                return m.obj
        if self.__load_python(module_name, class_name):
            return self.__module
        else:
            return self.__load_extension(module_name, class_name)

    def load_from_filename(self, filepath, modname):
        spec = importlib.util.spec_from_file_location(modname, filepath)
        self.__module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.__module)
        sys.modules[spec.name] = self.__module
        if self.__module is not None:
            self.__load_module_info(self.__module)
            return self.__module
        return None

    def __load_python(self, module_name, class_name):
        for pth in sys.path:
            modpath = module_name.replace(".", os.path.sep)
            modname = os.path.join(pth, modpath + ".py")
            if os.path.exists(modname):
                print("importing modname = ", modname)
                print("importing...")
                # for p in self.__search_path_list:
                self.__module = self.__import_helper(module_name)
                if self.__module is not None:
                    self.__load_module_info(self.__module)
                    return self.__module
        return None

    def __load_extension(self, module_name, class_name):
        modname = None
        for p in self.__search_path_list:
            if platform.system() == "Windows":
                modname = os.path.join(p, module_name + ".pyd")
            elif platform.system() == "Linux":
                modname = os.path.join(p, module_name + ".so")
            elif platform.system() == "Darwin":
                modname = os.path.join(p, module_name + ".so")
            if os.path.exists(modname):
                self.__module = self.__import_helper(p)
                self.__module_info_list.append(ModuleInfo(self.__module.__name__))
                return self.__module
        return None

    def __import_helper(self, pkg_path):
        import importlib
        # pkg = __name__.rpartition('.')[0]
        # mname = '.'.join((pkg_path, self.__module_name)).lstrip('.')
        try:
            return importlib.import_module(pkg_path)
        except ImportError:
            return importlib.import_module(self.__module_name)

    def __load_module_info(self, m):
        mi = ModuleInfo(m.__name__, m)
        for member, _type in inspect.getmembers(m):
            if member == "TransformStrategy":
                continue
            elif member == "InjectionStrategy":
                continue
            elif member == "DebugStrategy":
                continue
            if inspect.isclass(_type):
                cls = ClassInfo(member)
                mi.add_class(cls)
                self.__load_class_info(_type, cls)
            elif inspect.isfunction(_type):
                func = FunctionInfo(member)
                mi.add_function(func)
                self.__load_function_info(_type, func)
        self.__module_info_list.append(mi)

    def __load_class_info(self, c, ci):
        for member, _type in inspect.getmembers(c, predicate=inspect.isroutine):
            if member[0] == '_' and member[1] == '_':
                continue
            func = FunctionInfo(member)
            ci.add_function(func)
            self.__load_function_info(_type, func)

    def __load_function_info(self, f, fi):
        pass
