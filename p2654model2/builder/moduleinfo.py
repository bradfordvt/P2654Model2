#!/usr/bin/env python
"""
    Classes used to manage plugin module information.
    Copyright (C) 2021  Bradford G. Van Treuren

    ModuleInfo class describes a Python or Python wrapper module for interfacing to plugin strategies.
    ClassInfo class describes the names and methods of classes found in these ModuleInfo objects.
    FunctionInfo class describes the names of the methods in a Module or Class.

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
__date__ = "2021/02/06"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


class ModuleInfo(object):
    def __init__(self, name, obj):
        self.__obj = obj
        self.__name = name
        self.__classes = []
        self.__functions = []

    @property
    def name(self):
        return self.__name

    @property
    def obj(self):
        return self.__obj

    def get_class_names(self):
        cnames = []
        for c in self.__classes:
            cnames.append(c.name)
        return cnames

    def get_classes(self):
        return self.__classes

    def get_function_names(self):
        fnames = []
        for f in self.__functions:
            fnames.append(f.name)
        return fnames

    def get_functions(self):
        return self.__functions

    def add_class(self, cls):
        self.__classes.append(cls)

    def add_function(self, func):
        self.__functions.append(func)


class ClassInfo(object):
    def __init__(self, name):
        self.__name = name
        self.__functions = []

    @property
    def name(self):
        return self.__name

    def get_function_names(self):
        fnames = []
        for f in self.__functions:
            fnames.append(f.name)
        return fnames

    def get_functions(self):
        return self.__functions

    def add_function(self, func):
        self.__functions.append(func)


class FunctionInfo(object):
    def __init__(self, name):
        self.__name = name

    @property
    def name(self):
        return self.__name
