#!/usr/bin/env python
"""
    Builder class for building the tree model from a JSON based description.
    Copyright (C) 2021  Bradford G. Van Treuren

    Class to parse and build the software model of the UUT as a hierarchical tree as described
    in an associated JSON based description file.  The description is loosely based on the
    Simplified ICL Tree description proposed by Michele Portolan used by his MAST tool.

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

from p2654model2.error.ModelError import ModelError
from p2654model2.injection.injectorregistry import InjectorRegistry
from p2654model2.interface.accessinterface import AccessInterface
from p2654model2.interface.clientinterface import ClientInterface
from p2654model2.interface.hostinterface import HostInterface
from p2654model2.interface.testinjectioninterface import TestInjectionInterface
from p2654model2.node.injectionnode import InjectionNode
from p2654model2.node.modelnode import Root, Chain, ModelPoint, Instance, Register, Linker, Custom, Controller
from myhdl import intbv

from p2654model2.strategy.debug.debugstrategy import DebugStrategy
from p2654model2.strategy.inject.injectionstrategy import InjectionStrategy
from p2654model2.strategy.transform.transformstrategy import TransformStrategy


import logging
from autologging import traced, logged


module_logger = logging.getLogger('P2654Model2.builder.builder')


@logged
@traced
class Builder(object):
    inst = None

    @staticmethod
    def get_builder():
        if Builder.inst is None:
            Builder.inst = Builder()
        return Builder.inst

    def __init__(self):
        self.logger = logging.getLogger('P2654Model2.builder.builder')
        self.logger.info('Creating an instance of Builder')
        self.__filename = None
        self.__data = None

    def build_from_file(self, filename):
        self.__filename = filename
        with open(self.__filename) as model_data:
            self.__data = json.load(model_data)
        tree = self.__load_node(self.__data)
        return tree

    def build_from_file2(self, filename):
        self.__filename = filename
        tree = None
        with open(self.__filename) as model_data:
            self.__data = json.load(model_data)
        for key, value in self.__data.items():
            tree = self.__load_node(key, value)
            break
        return tree

    def build_from_string(self, model_data):
        self.__data = json.load(model_data)
        tree = None
        for key, value in self.__data.items():
            tree = self.__load_node(key, value)
            break
        return tree

    def __build_transform_strategy(self, node):
        if node.tstrategy is not None:
            strategy = TransformStrategy(node.name)
            strategy.register_node_uid(node.uid)
            strategy.register_tstrategy(node.tstrategy)
            cuids = []
            cnames = []
            for child in node.get_children():
                cuids.append(child.uid)
                cnames.append(child.name)
            strategy.register_child_uids(cuids)
            strategy.register_child_names(cnames)
            node.register_transform_strategy(strategy)
            strategy.create(node.transformParams)

    def __build_injection_strategy(self, node):
        if node.istrategy is not None:
            strategy = InjectionStrategy(node.name)
            strategy.register_node_uid(node.uid)
            strategy.register_istrategy(node.istrategy)
            cuids = []
            for child in node.get_children():
                cuids.append(child.uid)
            strategy.register_child_uids(cuids)
            node.register_injection_strategy(strategy)
            strategy.create(node.injectParams)

    def __build_debug_strategy(self, node):
        if node.dstrategy is not None:
            strategy = DebugStrategy(node.name)
            strategy.register_node_uid(node.uid)
            strategy.register_dstrategy(node.dstrategy)
            cuids = []
            for child in node.get_children():
                cuids.append(child.uid)
            strategy.register_child_uids(cuids)
            node.register_debug_strategy(strategy)
            strategy.create(node.debugParams)

    def __build_injectors(self, node):
        if node.injectors is None:
            return
        injectors = node.injectors
        testinjection_interface = TestInjectionInterface()
        test_access_interface = AccessInterface()
        node.register_testinjection_interface(testinjection_interface)
        for inj in injectors:
            for key in inj.keys():
                injector = self.__build_injector(key, node)  # inj is a string from injectors list
                testinjection_interface.registerAccessInterface(node.uid, test_access_interface)  # TODO - may need injector.iid instead
                injector.register_testinjection_interface(testinjection_interface)
                node.add_injector(injector)
                injector.create(inj[key])

    def __build_injector(self, injector, node):
        injector_node = InjectionNode(node.name, node.uid, node.transform_engine, injector, node.cproto)
        return injector_node

    def __load_node2(self, node):
        tree = None
        if node.get("ROOT"):
            tree = self.__load_root(node)
        elif node.get("CHAIN"):
            tree = self.__load_chain(node)
        elif node.get("LINKER"):
            tree = self.__load_linker(node)
        elif node.get("INSTANCE"):
            tree = self.__load_instance(node)
        elif node.get("MODELPOINT"):
            tree = self.__load_modelpoint(node)
        elif node.get("REGISTER"):
            tree = self.__load_register(node)
        elif node.get("CUSTOM"):
            tree = self.__load_custom(node)
        elif node.get("CONTROLLER"):
            tree = self.__load_controller(node)
        return tree

    def __load_node(self, key, value):
        tree = None
        lut = {"ROOT": self.__load_root,
               "CHAIN": self.__load_chain,
               "LINKER": self.__load_linker,
               "INSTANCE": self.__load_instance,
               "MODELPOINT": self.__load_modelpoint,
               "REGISTER": self.__load_register,
               "CUSTOM": self.__load_custom,
               "CONTROLLER": self.__load_controller}
        tree = lut[key](value)
        return tree

    def __load_root(self, node):
        # node = n.get("ROOT")
        children = node.get("children")
        tree = Root(node.get("name"))
        tree.hproto = node.get("hproto")
        tree.tstrategy = node.get("transform")
        tree.visible = node.get("visible")
        tree.configure()
        # access_interface = AccessInterface()
        # # test_access_interface = AccessInterface()
        # host_interface = HostInterface()
        # host_interface.registerAccessInterface(access_interface)
        # tree.register_host_interface(host_interface)
        # # testinjection_interface = TestInjectionInterface()
        # # testinjection_interface.registerAccessInterface(tree.uid, test_access_interface)
        # # tree.register_testinjection_interface(testinjection_interface)
        for child in children:
            for key, value in child.items():
                ctree = self.__load_node(key, value)
                # client_interface = ClientInterface()
                # client_interface.registerAccessInterface(access_interface)
                # ctree.register_client_interface(client_interface)
                tree.add_child(ctree)
        self.__build_transform_strategy(tree)
        self.__build_injection_strategy(tree)
        self.__build_debug_strategy(tree)
        self.__build_injectors(tree)
        return tree

    def __load_controller(self, node):
        # node = n.get("CONTROLLER")
        children = node.get("children")
        tree = Controller(node.get("name"))
        tree.hproto = node.get("hproto")
        tree.tstrategy = node.get("transform")
        tree.visible = node.get("visible")
        tree.configure()
        access_interface = AccessInterface()
        host_interface = HostInterface()
        host_interface.registerAccessInterface(access_interface)
        tree.register_host_interface(host_interface)
        for child in children:
            for key, value in child.items():
                ctree = self.__load_node(key, value)
                client_interface = ClientInterface()
                client_interface.registerAccessInterface(access_interface)
                ctree.register_client_interface(client_interface)
                tree.add_child(ctree)
        self.__build_transform_strategy(tree)
        self.__build_injection_strategy(tree)
        self.__build_debug_strategy(tree)
        self.__build_injectors(tree)
        return tree

    def __load_chain(self, node):
        # node = n.get("CHAIN")
        children = node.get("children")
        tree = Chain(node.get("name"))
        tree.cproto = node.get("cproto")
        tree.hproto = node.get("hproto")
        tree.tstrategy = node.get("transform")
        tree.injectors = node.get("injectors")
        tree.istrategy = node.get("istrategy")
        tree.dstrategy = node.get("debug")
        tree.transformParams = node.get("transformParams")
        tree.injectParams = node.get("injectParams")
        # tree.inodeParams = node.get("inodeParams")
        tree.visible = node.get("visible")
        tree.configure()
        access_interface = AccessInterface()
        # testinjection_interface = TestInjectionInterface()
        # test_access_interface = AccessInterface()
        host_interface = HostInterface()
        host_interface.registerAccessInterface(access_interface)
        tree.register_host_interface(host_interface)
        # tree.register_testinjection_interface(testinjection_interface)
        for child in children:
            for key, value in child.items():
                ctree = self.__load_node(key, value)
                client_interface = ClientInterface()
                client_interface.registerAccessInterface(access_interface)
                ctree.register_client_interface(client_interface)
                tree.add_child(ctree)
        # for inj in injectors:
        #     itree = self.__load_injector(inj, tree.uid, tree.injectParams)
        #     testinjection_interface.registerAccessInterface(test_access_interface)
        #     itree.register_testinjection_interface(testinjection_interface)
        #     itree.parameters = tree.inodeParams
        #     itree.configure()
        self.__build_transform_strategy(tree)
        self.__build_injection_strategy(tree)
        self.__build_debug_strategy(tree)
        self.__build_injectors(tree)
        return tree

    def __load_linker(self, node):
        # node = n.get("LINKER")
        children = node.get("children")
        tree = Linker(node.get("name"))
        tree.cproto = node.get("cproto")
        tree.hproto = node.get("hproto")
        tree.tstrategy = node.get("transform")
        tree.injectors = node.get("injectors")
        tree.istrategy = node.get("istrategy")
        tree.dstrategy = node.get("debug")
        tree.visible = node.get("visible")
        tree.selector = node.get("selector")
        tree.control = node.get("control")
        tree.derivations = node.get("derivations")
        tree.parameters = node.get("parameters")
        if node.get("transformParams") is None:
            node["transformParams"] = ""
        if node.get("injectParams") is None:
            node["injectParams"] = ""
        if node.get("inodeParams") is None:
            node["inodeParams"] = ""
        tree.transformParams = "selector={:s}, derivations={:s}, control={:s}, {:s}".format(str(node.get("selector")), str(node.get("derivations")), str(node.get("control")), str(node.get("transformParams")))
        tree.injectParams = "selector={:s}, derivations={:s}, control={:s}, {:s}".format(str(node.get("selector")), str(node.get("derivations")), str(node.get("control")), str(node.get("injectParams")))
        # tree.inodeParams = "selector={:s}, derivations={:s}, control={:s}, {:s}".format(str(node.get("selector")), str(node.get("derivations")), str(node.get("control")), str(node.get("inodeParams")))
        tree.configure()
        testinjection_interface = TestInjectionInterface()
        access_interface = AccessInterface()
        test_access_interface = AccessInterface()
        host_interface = HostInterface()
        host_interface.registerAccessInterface(access_interface)
        tree.register_host_interface(host_interface)
        testinjection_interface.registerAccessInterface(tree.uid, test_access_interface)
        tree.register_testinjection_interface(testinjection_interface)
        for child in children:
            for key, value in child.items():
                ctree = self.__load_node(key, value)
                client_interface = ClientInterface()
                client_interface.registerAccessInterface(access_interface)
                ctree.register_client_interface(client_interface)
                tree.add_child(ctree)
        # for inj in injectors:
        #     itree = self.__load_injector(inj, tree.uid, tree.injectParams)
        #     testinjection_interface.registerAccessInterface(test_access_interface)
        #     itree.register_testinjection_interface(testinjection_interface)
        #     itree.parameters = tree.inodeParams
        #     itree.configure()
        self.__build_transform_strategy(tree)
        self.__build_injection_strategy(tree)
        self.__build_debug_strategy(tree)
        self.__build_injectors(tree)
        return tree

    def __load_instance(self, node):
        # node = n.get("INSTANCE")
        tree = Instance(node.get("name"))
        tree.sit = node.get("sit")
        tree.factory = node.get("factory")
        tree.configure()
        newtree = self.__expand_instance(tree)
        return newtree

    def __load_modelpoint(self, node):
        # node = n.get("MODELPOINT")
        tree = ModelPoint(node.get("name"))
        tree.cproto = node.get("cproto")
        tree.tstrategy = node.get("transform")
        tree.dstrategy = node.get("debug")
        tree.visible = node.get("visible")
        tree.transformParams = node.get("transformParams")
        tree.configure()
        return tree

    def __load_register(self, node):
        # node = n.get("REGISTER")
        tree = Register(node.get("name"))
        tree.cproto = node.get("cproto")
        tree.size = int(node.get("size"))
        tree.visible = node.get("visible")
        safe = node.get("safe")
        if safe == "0":
            s = int(safe)
        elif safe[0] == '0' and safe[1] == 'x':
            s = int(safe, 16)
        elif safe[0] == '0' and safe[1] == 'b':
            s = int(safe, 2)
        else:
            s = int(safe)
        tree.safe = intbv(s, _nrbits=tree.size)
        tree.tstrategy = node.get("transform")
        tree.injectors = node.get("injectors")
        tree.istrategy = node.get("inject")
        tree.dstrategy = node.get("debug")
        tree.sticky = node.get("sticky")
        if node.get("transformParams") is None:
            node["transformParams"] = ""
        if node.get("injectParams") is None:
            node["injectParams"] = ""
        if node.get("inodeParams") is None:
            node["inodeParams"] = ""
        tree.transformParams = "size={:s}, safe={:s}, sticky={:s}, {:s}".format(str(node.get("size")), str(bin(tree.safe)), str(node.get("sticky")), str(node.get("transformParams")))
        tree.injectParams = "size={:s}, safe={:s}, sticky={:s}, {:s}".format(str(node.get("size")), str(bin(tree.safe)), str(node.get("sticky")), str(node.get("injectParams")))
        tree.inodeParams = "size={:s}, safe={:s}, sticky={:s}, {:s}".format(str(node.get("size")), str(bin(tree.safe)), str(node.get("sticky")), str(node.get("inodeParams")))
        tree.configure()
        # testinjection_interface = TestInjectionInterface()
        # test_access_interface = AccessInterface()
        # for inj in injectors:
        #     itree = self.__load_injector(inj, tree.uid, tree.injectParams)
        #     testinjection_interface.registerAccessInterface(test_access_interface)
        #     itree.register_testinjection_interface(testinjection_interface)
        #     itree.parameters = tree.inodeParams
        #     itree.configure()
        self.__build_transform_strategy(tree)
        self.__build_injection_strategy(tree)
        self.__build_debug_strategy(tree)
        self.__build_injectors(tree)
        return tree

    def __load_custom(self, node):
        # node = n.get("CUSTOM")
        children = node.get("children")
        tree = Custom(node.get("name"))
        tree.cproto = node.get("cproto")
        tree.hproto = node.get("hproto")
        tree.tstrategy = node.get("transform")
        tree.injectors = node.get("injectors")
        tree.istrategy = node.get("istrategy")
        tree.dstrategy = node.get("debug")
        tree.visible = node.get("visible")
        tree.selector = node.get("selector")
        tree.control = node.get("control")
        tree.derivations = int(node.get("derivations"))
        tree.parameters = node.get("parameters")
        if node.get("transformParams") is None:
            node["transformParams"] = ""
        if node.get("injectParams") is None:
            node["injectParams"] = ""
        if node.get("inodeParams") is None:
            node["inodeParams"] = ""
        tree.transformParams = "selector={:s}, derivations={:s}, control={:s}, {:s}".format(str(node.get("selector")), str(node.get("derivations")), str(node.get("control")), str(node.get("transformParams")))
        tree.injectParams = "selector={:s}, derivations={:s}, control={:s}, {:s}".format(str(node.get("selector")), str(node.get("derivations")), str(node.get("control")), str(node.get("injectParams")))
        tree.inodeParams = "selector={:s}, derivations={:s}, control={:s}, {:s}".format(str(node.get("selector")), str(node.get("derivations")), str(node.get("control")), str(node.get("inodeParams")))
        tree.configure()
        access_interface = AccessInterface()
        # testinjection_interface = TestInjectionInterface()
        # test_access_interface = AccessInterface()
        host_interface = HostInterface()
        host_interface.registerAccessInterface(access_interface)
        tree.register_host_interface(host_interface)
        # tree.register_testinjection_interface(tree.uid, testinjection_interface)
        for child in children:
            for key, value in child.items():
                ctree = self.__load_node(key, value)
                client_interface = ClientInterface()
                client_interface.registerAccessInterface(access_interface)
                ctree.register_client_interface(client_interface)
                tree.add_child(ctree)
        # for inj in injectors:
        #     itree = self.__load_injector(inj, tree.uid, tree.injectParams)
        #     testinjection_interface.registerAccessInterface(test_access_interface)
        #     itree.register_testinjection_interface(testinjection_interface)
        #     itree.parameters = tree.inodeParams
        #     itree.configure()
        self.__build_transform_strategy(tree)
        self.__build_injection_strategy(tree)
        self.__build_debug_strategy(tree)
        self.__build_injectors(tree)
        return tree

    def __expand_instance(self, instance):
        if instance.sit:
            builder = Builder()
            return builder.build_from_file(instance.sit)
        elif instance.factory:
            raise ModelError("INSTANCE with factory is not supported yet.")
        raise ModelError("INSTANCE not configured correctly.")

    def __load_injector(self, injector, uid, params):
        ireg = InjectorRegistry.getRegistry()
        injcls = ireg.get_injector(injector)
        if injcls is None:
            raise ModelError("Unable to locate injector ({:s}).".format(injector))
        injobj = injcls(injector, uid, params)
        ireg.add_instance(injobj)
        return injobj
