#!/usr/bin/env python
"""
    Classes representing specialized ModelNodes of the hierarchical tree description model.
    Copyright (C) 2021  Bradford G. Van Treuren

    Classes representing specialized ModelNodes of the hierarchical tree description model.
    ModelNode: Base class of all types of model nodes in the hierarchical tree.
    Register: Specialized ModelNode describing a REGISTER building block.
    Instance: Specialized ModelNode describing an INSTANCE building block.
    Chain: Specialized ModelNode describing a CHAIN building block.
    Linker: Specialized ModelNode describing a LINKER building block.
    ModelPoint: Specialized ModelNode describing a MODELPOINT building block.
    Custom: Specialized ModelNode describing a CUSTOM building block.
    Controller: Specialized ModelNode describing a CONTROLLER building block.
    Root: Specialized ModelNode describing a ROOT building block.

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
__date__ = "2021/01/14"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


from enum import Enum
from p2654model2.builder.moduleloader import ModuleLoader
from p2654model2.builder.nodecontainer import NodeContainer
from p2654model2.error.ModelError import ModelError
# from p2654model2.interface.clientinterface import ClientInterface
# from p2654model2.interface.hostinterface import HostInterface
from p2654model2.node.PathState import PathState
from p2654model2.node.transformengine import TransformEngine


import logging
from autologging import traced, logged


module_logger = logging.getLogger('p2654model2.node.modelnode')


class NodeTypes(Enum):
    UNKNOWN = 0
    REGISTER = 1
    CHAIN = 2
    LINKER = 3
    MODELPOINT = 4
    INSTANCE = 5
    CUSTOM = 6


@logged
@traced
class ModelNode(object):
    class Actions(Enum):
        NO_ACTION = 0
        ACTIVATE_PATH = 1
        DEACTIVATE_PATH = 2

    class NodeType(Enum):
        LEAF = 0
        MODELPOINT = 1
        TRANSFORM = 2

    class Flow(Enum):
        TRANSFORM = 0
        INJECTION = 1

    __indent = 0

    # def __init__(self, name, depth_next):
    def __init__(self, name, node_type):
        self.logger = logging.getLogger('p2654model2.node.modelnode')
        self.logger.info('Creating an instance of ModelNode')
        self.node_type = NodeTypes.UNKNOWN
        # self.__uid = None  # universal identifier as int
        # self.__name = name
        self.__cproto = None
        self.__hproto = None
        # self.__tstrategy = None
        self.__injectors = None
        # self.__istrategy = None
        # self.__dstrategy = None
        # self.__cstrategy = None
        self.__visible = False
        # self.__transformParams = None
        # self.__injectParams = None
        # self.__debugParams = None
        # self.__inodeParams = None
        # ##############################
        # self.__transform_strategy = None
        # self.__inject_strategy = None
        # self.__debug_strategy = None
        # self.__custom_strategy = None
        # ##############################
        # self._client_interface = None
        # self._host_interface = None
        # self._testinection_interface = None
        self.__transform_engine = TransformEngine(name, node_type)
        # self._breadth_next = None  # Reference to next 'brother' segment
        # self._depth_ref = None
        # self.depth_next = depth_next  # reference to the procedure that handles the tree descent
        self.__path_state = PathState.INACTIVE
        self.__inodeParams = None
        nc = NodeContainer.get_nodecontainer()
        nc.add_node(self)

    # def depth(self):
    #     return self._depth_ref
    #
    # def breadth(self):
    #     return self._breadth_next
    #
    # def depth_next(self):
    #     action = ModelNode.Actions.NO_ACTION
    #     ret = None
    #     if isinstance(self, Linker):
    #         if self.path_state == PathState.ACTIVE:
    #             ret = self._depth_ref
    #         elif self.path_state == PathState.INACTIVE:
    #             pass
    #         else:
    #             # unreachable
    #             pass
    #         action = self.explore_cross_subpath()
    #     return ret, action
    #
    # def explore_cross_subpath(self):
    #     # default action
    #     action = ModelNode.Actions.DEACTIVATE_PATH
    #     return action

    def apply(self, timeout):
        return self.__transform_engine.apply(timeout)

    def add_child(self, child):
        self.__transform_engine.add_model_child(child)

    def add_injector(self, injector):
        self.__transform_engine.add_injector_child(injector)

    def get_children(self):
        return self.__transform_engine.get_children()

    def get_status(self):
        return self.__transform_engine.get_status()

    def get_error(self):
        return self.__transform_engine.get_error()

    def get_data_value(self):
        return self.__transform_engine.get_data_value()

    def register_client_interface(self, client_interface):
        client_interface.registerTransformEngine(self.__transform_engine)
        client_interface.set_resp_callback(self.uid, client_interface.handleResponse)
        client_interface.set_update_req_callback(self.uid, client_interface.handleUpdateRequest)
        client_interface.set_update_resp_callback(self.uid, client_interface.handleUpdateResponse)
        self.__transform_engine.registerClientInterface(client_interface)

    def register_host_interface(self, host_interface):
        host_interface.registerTransformEngine(self.__transform_engine)
        host_interface.set_req_callback(self.uid, host_interface.handleRequest)
        self.__transform_engine.registerHostInterface(host_interface)

    def register_testinjection_interface(self, testinection_interface):
        testinection_interface.registerTransformEngine(self.__transform_engine)
        # testinection_interface.set_req_callback(self.uid, testinection_interface.handleRequest)
        self.__transform_engine.registerTestInjectionInterface(testinection_interface)

    ########## External Builder support #
    def register_transform_strategy(self, transform_strategy):
        # transform_strategy.register_transform_engine(self.__transform_engine)
        self.__transform_engine.register_transform_strategy(transform_strategy)

    def register_injection_strategy(self, injection_strategy):
        self.__transform_engine.registerInjectionStrategy(injection_strategy)

    @property
    def transform_engine(self):
        return self.__transform_engine

    @property
    def uid(self):
        return self.__transform_engine.uid

    # @uid.setter
    # def uid(self, uid):
    #     if not isinstance(uid, int):
    #         raise ModelError("uid is not of type int.")
    #     self.__transform_engine.uid = uid

    @property
    def name(self):
        return self.__transform_engine.name

    @name.setter
    def name(self, name):
        self.__transform_engine.name = name

    @property
    def cproto(self):
        return self.__cproto

    @cproto.setter
    def cproto(self, cproto):
        self.__cproto = cproto

    @property
    def hproto(self):
        return self.__hproto

    @hproto.setter
    def hproto(self, hproto):
        self.__hproto = hproto

    @property
    def tstrategy(self):
        return self.__transform_engine.tstrategy

    @tstrategy.setter
    def tstrategy(self, tstrategy):
        self.__transform_engine.tstrategy = tstrategy

    @property
    def injectors(self):
        return self.__injectors

    @injectors.setter
    def injectors(self, injectors):
        self.__injectors = injectors

    @property
    def istrategy(self):
        return self.__transform_engine.istrategy

    @istrategy.setter
    def istrategy(self, istrategy):
        self.__transform_engine.istrategy = istrategy

    @property
    def dstrategy(self):
        return self.__transform_engine.dstrategy

    @dstrategy.setter
    def dstrategy(self, dstrategy):
        self.__transform_engine.dstrategy = dstrategy

    @property
    def cstrategy(self):
        return self.__transform_engine.cstrategy

    @cstrategy.setter
    def cstrategy(self, cstrategy):
        self.__transform_engine.cstrategy = cstrategy

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, visible):
        self.__visible = visible

    @property
    def transformParams(self):
        return self.__transform_engine.transformParams

    @transformParams.setter
    def transformParams(self, transformParams):
        self.__transform_engine.transformParams = transformParams

    @property
    def injectParams(self):
        return self.__transform_engine.injectParams

    @injectParams.setter
    def injectParams(self, injectParams):
        self.__transform_engine.injectParams = injectParams

    @property
    def debugParams(self):
        return self.__transform_engine.debugParams

    @debugParams.setter
    def debugParams(self, debugParams):
        self.__transform_engine.debugParams = debugParams

    @property
    def inodeParams(self):
        return self.__transform_engine.inodeParams

    @inodeParams.setter
    def inodeParams(self, inodeParams):
        self.__transform_engine.inodeParams = inodeParams

    @property
    def path_state(self):
        return self.__path_state

    @path_state.setter
    def path_state(self, state):
        if not isinstance(state, PathState):
            raise ModelError("state is not an ModelNode.PathState.")
        self.__path_state = state

    def configure(self):
        self.__transform_engine.configure()
    #     self.__transform_engine = TransformEngine(self.__name, self.__uid,
    #                                               self.tstrategy, self.__transformParams,
    #                                               self.istrategy, self.__injectParams,
    #                                               self.dstrategy, self.debugParams)

    def handleCommand(self, wrapper):
        return self.__transform_engine.handleCommand(wrapper)

    def get_command_id(self, command):
        return self.__transform_engine.get_command_id(command)

    def indent(self):
        ModelNode.__indent += 4

    def dedent(self):
        ModelNode.__indent -= 4

    def writeln(self, ln):
        print(" " * ModelNode.__indent, ln)

    def dump_base(self):
        self.writeln("uid = {:d}".format(self.uid))
        self.writeln("cproto = {:s}".format(str(self.cproto)))
        self.writeln("hproto = {:s}".format(str(self.hproto)))
        self.writeln("tstrategy = {:s}".format(str(self.tstrategy)))
        self.writeln("istrategy = {:s}".format(str(self.istrategy)))
        self.writeln("dstrategy = {:s}".format(str(self.dstrategy)))
        self.writeln("cstrategy = {:s}".format(str(self.cstrategy)))
        self.writeln("visible = {:s}".format(str(self.visible)))
        self.writeln("transformParams = {:s}".format(str(self.transformParams)))
        self.writeln("injectParams = {:s}".format(str(self.injectParams)))
        self.writeln("debugParams = {:s}".format(str(self.debugParams)))
        self.writeln("inodeParams = {:s}".format(str(self.inodeParams)))
        self.__transform_engine.dump(ModelNode.__indent)


@logged
@traced
class Register(ModelNode):
    def __init__(self, name):
        self.logger = logging.getLogger('p2654model2.node.modelnode')
        self.logger.info('Creating an instance of Register')
        super(Register, self).__init__(name, TransformEngine.NodeType.LEAF)
        self.__size = 0
        self.__safe = None
        self.__sticky = False

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        self.__size = size

    @property
    def safe(self):
        return self.__safe

    @safe.setter
    def safe(self, safe):
        self.__safe = safe

    @property
    def sticky(self):
        return self.__sticky

    @sticky.setter
    def sticky(self, sticky):
        self.__sticky = sticky

    def get_value(self):
        return super().get_data_value()

    def dump(self):
        self.writeln("Dumping Register ({:s})".format(str(self.name)))
        self.indent()
        self.writeln("size = {:d}".format(self.size))
        self.writeln("safe = {:s}".format(str(self.safe)))
        self.writeln("sticky = {:s}".format(str(self.sticky)))
        self.dump_base()
        self.dedent()


@logged
@traced
class Instance(ModelNode):
    def __init__(self, name):
        self.logger = logging.getLogger('p2654model2.node.modelnode')
        self.logger.info('Creating an instance of Instance')
        super(Instance, self).__init__(name, TransformEngine.NodeType.TRANSFORM)
        self.__sit = None
        self.__factory = None

    @property
    def sit(self):
        return self.__sit

    @sit.setter
    def sit(self, sit):
        self.__sit = sit

    @property
    def factory(self):
        return self.__factory

    @factory.setter
    def factory(self, factory):
        self.__factory = factory

    def dump(self):
        self.writeln("Dumping Instance ({:s})".format(str(self.name)))
        self.indent()
        self.writeln("sit = {:s}".format(str(self.sit)))
        self.writeln("factory = {:s}".format(str(self.factory)))
        self.dump_base()
        self.dedent()


@logged
@traced
class Chain(ModelNode):
    def __init__(self, name):
        self.logger = logging.getLogger('p2654model2.node.modelnode')
        self.logger.info('Creating an instance of Chain')
        super(Chain, self).__init__(name, TransformEngine.NodeType.TRANSFORM)

    def dump(self):
        self.writeln("Dumping Chain ({:s})".format(str(self.name)))
        self.indent()
        self.dump_base()
        self.dedent()


@logged
@traced
class Linker(ModelNode):
    def __init__(self, name):
        self.logger = logging.getLogger('p2654model2.node.modelnode')
        self.logger.info('Creating an instance of Linker')
        super(Linker, self).__init__(name, TransformEngine.NodeType.TRANSFORM)
        self.__selector = None
        self.__control = []
        self.__derivations = 0
        self.__parameters = None

    @property
    def selector(self):
        return self.__selector

    @selector.setter
    def selector(self, selector):
        self.__selector = selector

    @property
    def derivations(self):
        return self.__derivations

    @derivations.setter
    def derivations(self, derivations):
        self.__derivations = derivations

    @property
    def control(self):
        return self.__control

    @control.setter
    def control(self, control):
        self.__control = control

    @property
    def parameters(self):
        return self.__parameters

    @parameters.setter
    def parameters(self, parameters):
        self.__parameters = parameters

    def dump(self):
        self.writeln("Dumping Linker ({:s})".format(str(self.name)))
        self.indent()
        self.writeln("selector = {:s}".format(str(self.selector)))
        self.writeln("derivations = {:d}".format(self.__derivations))
        self.writeln("parameters = {:s}".format(str(self.parameters)))
        if len(self.control):
            for c in self.control:
                self.writeln("control = {:s}".format(str(self.control)))
        else:
            self.writeln("control = []")
        self.dump_base()
        self.dedent()


@logged
@traced
class ModelPoint(ModelNode):
    def __init__(self, name):
        self.logger = logging.getLogger('p2654model2.node.modelnode')
        self.logger.info('Creating an instance of ModelPoint')
        super(ModelPoint, self).__init__(name, TransformEngine.NodeType.MODELPOINT)

    def dump(self):
        self.writeln("Dumping ModelPoint ({:s})".format(str(self.name)))
        self.indent()
        self.dump_base()
        self.dedent()


@logged
@traced
class Custom(ModelNode):
    def __init__(self, name, flow_type=TransformEngine.NodeType.TRANSFORM):
        self.logger = logging.getLogger('p2654model2.node.modelnode')
        self.logger.info('Creating an instance of Custom')
        super(Custom, self).__init__(name, flow_type)
        self.__selector = None
        self.__control = []
        self.__derivations = 0
        self.__parameters = None

    @property
    def selector(self):
        return self.__selector

    @selector.setter
    def selector(self, selector):
        self.__selector = selector

    @property
    def derivations(self):
        return self.__derivations

    @derivations.setter
    def derivations(self, derivations):
        self.__derivations = derivations

    @property
    def control(self):
        return self.__control

    @control.setter
    def control(self, control):
        self.__control = control

    @property
    def parameters(self):
        return self.__parameters

    @parameters.setter
    def parameters(self, parameters):
        self.__parameters = parameters

    def dump(self):
        self.writeln("Dumping Custom ({:s})".format(str(self.name)))
        self.indent()
        self.writeln("selector = {:s}".format(str(self.selector)))
        self.writeln("derivations = {:d}".format(self.__derivations))
        self.writeln("parameters = {:s}".format(str(self.parameters)))
        for c in self.control:
            self.writeln("control = {:s}".format(str(self.control)))
        self.dump_base()
        self.dedent()


@logged
@traced
class Controller(ModelNode):
    def __init__(self, name):
        self.logger = logging.getLogger('p2654model2.node.modelnode')
        self.logger.info('Creating an instance of Controller')
        super(Controller, self).__init__(name, TransformEngine.NodeType.TRANSFORM)

    def dump(self):
        self.writeln("Dumping Controller ({:s})".format(str(self.name)))
        self.indent()
        self.dump_base()
        self.dedent()


@logged
@traced
class Root(ModelNode):
    def __init__(self, name):
        self.logger = logging.getLogger('p2654model2.node.modelnode')
        self.logger.info('Creating an instance of Root')
        super(Root, self).__init__(name, TransformEngine.NodeType.TRANSFORM)

    def dump(self):
        self.writeln("Dumping Root ({:s})".format(str(self.name)))
        self.indent()
        self.dump_base()
        self.dedent()
