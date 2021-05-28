#!/usr/bin/env python
"""
    Class to configure the runtime environment for the tooling.
    Copyright (C) 2021  Bradford G. Van Treuren

    Class to configure the runtime environment for the tooling.

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
__date__ = "2021/02/11"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


import json
import os

from p2654model2.builder.moduleloader import ModuleLoader


class Configurer(object):
    inst = None

    @staticmethod
    def get_configurer():
        if Configurer.inst is None:
            Configurer.inst = Configurer()
        return Configurer.inst

    def __init__(self):
        self.__config_file = None
        self.__data = None
        self.__load_defaults()

    def load(self, filename):
        self.__config_file = filename
        with open(self.__config_file) as model_data:
            self.__data = json.load(model_data)
        self.__load_searchpaths()
        self.__load_strategies()
        self.__load_injectors()

    def __load_searchpaths(self):
        spaths = None
        try:
            spaths = self.__data["searchpaths"]
        except KeyError:
            return
        ml = ModuleLoader.get_moduleloader()
        for p in spaths:
            ml.add_sys_path(p["path"])

    def __load_strategies(self):
        '''
        {
          "strategies" : [
            { "module": "P2654Model2.strategy.transform.strategies.dummytstrategy",
              "class": "dummytstrategy" },
            { "module": "<module1>",
              "class": "<class name>" },
            { "module": "<module2>"
              "class": "<class name>" }
            ]
        }
        :return:
        '''
        strategies = None
        try:
            strategies = self.__data["strategies"]
        except KeyError:
            return
        ml = ModuleLoader.get_moduleloader()
        for s in strategies:
            minfo = ml.get_module_info(s["module"])
            if minfo is None:
                _module = ml.load(s["module"], s["class"])
                minfo = ml.get_module_info(s["module"])
                class_names = minfo.get_class_names()
                if s["class"] not in class_names:
                    raise SyntaxError("strategy class {:s} not found in {:s}.".format(s["class"], s["module"]))
            else:
                class_names = minfo.get_class_names()
                if s["class"] not in class_names:
                    raise SyntaxError("strategy class {:s} not found in {:s}.".format(s["class"], s["module"]))

    def __load_injectors(self):
        '''
        {
          "injectors" : [
            { "module": "<module1>",
              "class": "<class name>" },
            { "module": "<module2>",
              "class": "<class name>" }
            ]
        }
        :return:
        '''
        injectors = None
        try:
            injectors = self.__data["injectors"]
        except KeyError:
            return
        ml = ModuleLoader.get_moduleloader()
        for inj in injectors:
            minfo = ml.get_module_info(inj["module"])
            if minfo is None:
                _module = ml.load(inj["module"], inj["class"])
                minfo = ml.get_module_info(inj["module"])
                class_names = minfo.get_class_names()
                if inj["class"] not in class_names:
                    raise SyntaxError("injector class {:s} not found in {:s}.".format(inj["class"], inj["module"]))
            else:
                class_names = minfo.get_class_names()
                if inj["class"] not in class_names:
                    raise SyntaxError("injector class {:s} not found in {:s}.".format(inj["class"], inj["module"]))

    def __load_debuggers(self):
        '''
        {
          "debuggers" : [
            { "module": "<module1>",
              "class": "<class name>" },
            { "module": "<module2>",
              "class": "<class name>" }
            ]
        }
        :return:
        '''
        debuggers = None
        try:
            debuggers = self.__data["debuggers"]
        except KeyError:
            return
        ml = ModuleLoader.get_moduleloader()
        for dbg in debuggers:
            minfo = ml.get_module_info(dbg["module"])
            if minfo is None:
                _module = ml.load(dbg["module"], dbg["class"])
                minfo = ml.get_module_info(dbg["module"])
                class_names = minfo.get_class_names()
                if dbg["class"] not in class_names:
                    raise SyntaxError("debugger class {:s} not found in {:s}.".format(dbg["class"], dbg["module"]))
            else:
                class_names = minfo.get_class_names()
                if dbg["class"] not in class_names:
                    raise SyntaxError("debugger class {:s} not found in {:s}.".format(dbg["class"], dbg["module"]))

    def __load_defaults(self):
        strategies_path = os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), "strategy"), "transform"), "strategies")
        module_path = "P2654Model2.strategy.transform.strategies"
        strategies_path2 = os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), "strategy"), "inject"), "strategies")
        module_path2 = "P2654Model2.strategy.inject.strategies"
        strategies_path3 = os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), "strategy"), "debug"), "strategies")
        module_path3 = "P2654Model2.strategy.debug.strategies"
        ml = ModuleLoader.get_moduleloader()
        ml.add_search_path_list(module_path)
        ml.add_sys_path(strategies_path)
        ml.add_search_path_list(module_path2)
        ml.add_sys_path(strategies_path2)
        ml.add_search_path_list(module_path3)
        ml.add_sys_path(strategies_path3)

