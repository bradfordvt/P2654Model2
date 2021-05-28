#!/usr/bin/env python
"""
    TransformEngine class is used to route messages inside of a ModelNode.
    Copyright (C) 2021  Bradford G. Van Treuren

    TransformEngine class is used to route messages inside of a ModelNode.

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
from p2654model2.scheduler.scheduler import SchedulerFactory
from p2654model2.strategy.inject.injectionstrategy import InjectionStrategy
from p2654model2.strategy.transform.transformstrategy import TransformStrategy
import p2654model2.rvf.rvfmessage_pb2


import logging
from autologging import traced, logged


module_logger = logging.getLogger('p2654model2.node.transformengine')


@logged
@traced
class TransformEngine(object):
    # global_uid = 0
    __indent = 0

    class NodeType(Enum):
        LEAF = 0
        MODELPOINT = 1
        TRANSFORM = 2

    class Flow(Enum):
        TRANSFORM = 0
        INJECTION = 1

    def __init__(self, name, node_type):
        self.logger = logging.getLogger('p2654model2.node.transformengine')
        self.logger.info('Creating an instance of TransformEngine({:s})'.format(name))
        # global global_uid
        # self.__uid = global_uid  # universal identifier as int
        nc = NodeContainer.get_nodecontainer()
        self.__uid = nc.get_next_node_id()  # universal identifier as int
        # global_uid += 1
        self.__name = name
        # self.__cproto = None
        # self.__hproto = None
        self.__tstrategy = None
        self.__inj_models = None
        self.__istrategy = None
        self.__dstrategy = None
        self.__cstrategy = None
        # self.__visible = False
        self.__transformParams = None
        self.__injectParams = None
        self.__debugParams = None
        self.__inodeParams = None
        ##############################
        self.__transform_strategy = None
        self.__injection_strategy = None
        self.__debug_strategy = None
        self.__custom_strategy = None
        ##############################
        self._client_interface = None
        self._host_interface = None
        self._testinjection_interface = None
        self.__status = "OK"
        self.__error = "UNKNOWN"
        # self.name = name
        # self.uid = uid
        # self.tstrategy = tstrategy
        # self.istrategy = istrategy
        # self.dstrategy = dstrategy
        # self.tparam = tparams
        # self.iparams = iparams
        # self.dparams = dparams
        # self.__transform_strategy = None
        # self.__injection_strategy = None
        # self.__debug_strategy = None
        # self.__client_interface = None
        # self.__host_interface = None
        # self.__testinjection_interface = None
        self.__flow = TransformEngine.Flow.TRANSFORM
        self.__node_type = node_type
        self.__model_children = []
        self.__children_uids = []
        self.__children_names = []
        self.__injection_children = []
        self.__injection_iids = []
        self.data_value = None
        self.__observers = []

    def add_model_child(self, child):
        self.__model_children.append(child)
        self.__children_uids.append(child.uid)
        self.__children_names.append(child.name)

    def add_injector_child(self, child):
        self.__injection_children.append(child)
        self.__injection_iids.append(child.iid)

    def get_status(self):
        lstat = self.__status
        self.__status = "OK"
        return lstat

    def get_error(self):
        lerr = self.__error
        self.__error = "UNKNOWN"
        return lerr

    def handleModelRequest(self, message):
        self.logger.debug("TransformEngine.handleModelRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        if self.__transform_strategy is None:
            raise ModelError("transform_strategy not registered for {:s}.".format(self.name))
        else:
            self.__flow = TransformEngine.Flow.TRANSFORM
            SchedulerFactory.get_scheduler().mark_pending()
            ret = self.__transform_strategy.handleRequest(message)
            if ret is not None:
                rvf = self.__transform_strategy.getStatus()
                if rvf is not None:
                    self.__status = rvf.message
                    return True
                    # return rvf
                else:
                    rvf = self.__transform_strategy.getError()
                    # rvf is a p2654model2.rvf.protocols.RVFMessage_pb2.ERROR()
                    self.__status = rvf.message
                    if self.__status == "OK":
                        return True
                    else:
                        SchedulerFactory.get_scheduler().clear_pending()
                        return False
            else:
                rvf = self.__transform_strategy.getError()
                if rvf is not None:
                    # rvf is a p2654model2.rvf.protocols.RVFMessage_pb2.ERROR()
                    self.__error = rvf.message
                    SchedulerFactory.get_scheduler().clear_pending()
                    return False
                else:
                    SchedulerFactory.get_scheduler().clear_pending()
                    return None

    def handleInjectionRequest(self, message):
        self.logger.debug("TransformEngine.handleInjectionRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        if self.__injection_strategy is None:
            raise ModelError("injection_strategy not registered for {:s}.".format(self.name))
        else:
            SchedulerFactory.get_scheduler().mark_pending()
            self.__flow = TransformEngine.Flow.INJECTION
            ret = self.__injection_strategy.handleRequest(message)
            if ret is not None:
                rvf = self.__injection_strategy.getStatus()
                if rvf is not None:
                    # rvf is a p2654model2.rvf.protocols.RVFMessage_pb2.STATUS()
                    self.__status = rvf.message
                    if self.__status == "OK":
                        return True
                    else:
                        SchedulerFactory.get_scheduler().clear_pending()
                        return False
                else:
                    rvf = self.__injection_strategy.getError()
                    if rvf is not None:
                        # rvf is a p2654model2.rvf.protocols.RVFMessage_pb2.ERROR()
                        self.__error = rvf.message
                        SchedulerFactory.get_scheduler().clear_pending()
                        return False
                    else:
                        SchedulerFactory.get_scheduler().clear_pending()
                        return None
            else:
                rvf = self.__injection_strategy.getError()
                if rvf is not None:
                    # rvf is a p2654model2.rvf.protocols.RVFMessage_pb2.ERROR()
                    self.__error = rvf.message
                    SchedulerFactory.get_scheduler().clear_pending()
                    return False
                else:
                    SchedulerFactory.get_scheduler().clear_pending()
                    return None

    def handleResponse(self, message):
        self.logger.debug("TransformEngine.handleResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        if self.__flow == TransformEngine.Flow.TRANSFORM:
            ret = self.__transform_strategy.handleResponse(message)
            # SchedulerFactory.get_scheduler().clear_pending()
            return ret
        elif self.__flow == TransformEngine.Flow.INJECTION:
            ret = self.__injection_strategy.handleResponse(message)
            # SchedulerFactory.get_scheduler().clear_pending()
            return ret

    def handleUpdateRequest(self, message):
        self.logger.debug("TransformEngine.handleUpdateRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        # SchedulerFactory.get_scheduler().mark_pending()
        return self.__transform_strategy.updateRequest(message)

    def handleUpdateResponse(self, message):
        self.logger.debug("TransformEngine.handleUpdateResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        ret = self.__transform_strategy.updateResponse(message)
        # SchedulerFactory.get_scheduler().clear_pending()
        return ret

    def sendRequest(self, message):
        self.logger.debug("TransformEngine.sendRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        ret = self._client_interface.sendRequest(message)
        SchedulerFactory.get_scheduler().clear_pending()
        return ret

    def sendResponse(self, message):
        self.logger.debug("TransformEngine.sendResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        if self.__flow == TransformEngine.Flow.TRANSFORM:
            ret = self._host_interface.sendResponse(message)
            SchedulerFactory.get_scheduler().clear_pending()
            return ret
        elif self.__flow == TransformEngine.Flow.INJECTION:
            ret = self._testinjection_interface.sendResponse(message)
            SchedulerFactory.get_scheduler().clear_pending()
            return ret

    def updateRequest(self, message):
        self.logger.debug("TransformEngine.updateRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        if self.__node_type == TransformEngine.NodeType.LEAF or self.__node_type == TransformEngine.NodeType.MODELPOINT:
            # SchedulerFactory.get_scheduler().mark_pending()
            return self.__transform_strategy.updateRequest(message)
        else:
            # SchedulerFactory.get_scheduler().mark_pending()
            return self._host_interface.updateRequest(message)

    def updateResponse(self, message):
        self.logger.debug("TransformEngine.updateResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        if self.__node_type == TransformEngine.NodeType.LEAF or self.__node_type == TransformEngine.NodeType.MODELPOINT:
            ret = self.__transform_strategy.updateResponse(message)
            SchedulerFactory.get_scheduler().clear_pending()
            return ret
        else:
            ret = self._host_interface.updateResponse(message)
            SchedulerFactory.get_scheduler().clear_pending()
            return ret

    def updateDataValue(self, message):
        self.data_value = message.data
        # TBD - send notification to observers for state change event on this node value
        if len(self.__observers):
            nc = NodeContainer.get_nodecontainer()
            obsmsg = p2654model2.rvf.rvfmessage_pb2.RVFSelectEvent()
            my_path = nc.get_path_by_id(self.uid)
            obsmsg.path = my_path
            for v in message.data:
                obsmsg.data.append(v)
            for obs_id in self.__observers:
                obs_node = nc.get_node_by_id(obs_id)
                ote = obs_node.transform_engine
                ote.update_observer(obsmsg)

    def update_observer(self, message):
        return self.__transform_strategy.update_observer(message)

    def apply(self, timeout):
        pending = 0
        err = 0
        self.logger.debug("TransformEngine.apply({:s}): processing\n".format(self.name))
        r = self.__applyInjection(timeout)
        if r == 1:
            pending += 1
        elif r == -1:
            err += 1
        r = self.__applyModel(timeout)
        if r == 1:
            pending += 1
        elif r == -1:
            err += 1
        if err:
            return -1
        elif pending:
            return 1
        else:
            return 0

    def handleCommand(self, wrapper):
        self.logger.debug("TransformEngine.handleCommand({:s}): processing {:s} RVF\n".format(self.name, wrapper.metaname))
        for node in self.__injection_children:
            if node.iid == wrapper.IID:
                return node.handleCommand(wrapper)
        return False

    def get_command_id(self, command):
        for node in self.__injection_children:
            commands = node.get_commands()
            if command in commands:
                return node.iid
        return None

    # def registerTransformStrategy(self, transform_strategy):
    #     self.__transform_strategy = transform_strategy
    #
    def registerInjectionStrategy(self, injection_strategy):
        self.__injection_strategy = injection_strategy

    def registerDebugStrategy(self, debug_strategy):
        self.__debug_strategy = debug_strategy

    def registerClientInterface(self, client_interface):
        self._client_interface = client_interface

    def registerHostInterface(self, host_interface):
        self._host_interface = host_interface

    def registerTestInjectionInterface(self, testinjection_interface):
        self._testinjection_interface = testinjection_interface

    ############ To support build
    def register_transform_strategy(self, transform_strategy):
        self.__transform_strategy = transform_strategy

    def register_observer(self, node_uid):
        """
        Used to register Linker selectors using this node as a selector.
        Need to notify Linker of register value changes during the execution
        of update_data_value() call.  What is sent is a data value message that
        could be a number of different data types.
        :param node_uid: Node_uid from Linker TransformStrategy to call
                realize the event change of the selector.
        :return:
        """
        self.__observers.append(node_uid)

    def get_name(self):
        return self.name

    def get_children(self):
        return self.__model_children

    def configure(self):
        ret = True
        for seg in self.__model_children:
            if not seg.configure():
                ret = False
        if self.__transform_strategy is not None:
            if not self.__transform_strategy.configure():
                ret = False
        else:
            self.logger.debug("TransformEngine.configure(): self.__transform_strategy is not defined for ({:s}).\n".format(self.name))
        return ret

    # def configure(self):
    #     self.__configure_transform()
    #     self.__configure_injection()
    #     self.__configure_injector()
    #     self.__configure_debug()
    #
    # def __configure_transform(self):
    #     if self.tstrategy:
    #         self.__transform_strategy = TransformStrategy(self.__name, self,
    #                                                       self.tstrategy,
    #                                                       self.__uid,
    #                                                       self.__model_children)
    #         self.__transform_strategy.create(self.__transformParams)
    #
    # def __configure_injection(self):
    #     if self.istrategy:
    #         self.__injection_strategy = InjectionStrategy(self.__name, self,
    #                                                       self.istrategy,
    #                                                       self.__uid,
    #                                                       self.__injection_iids,
    #                                                       self.__children_uids)
    #
    #         self.__transform_strategy.create(self.__injectParams)
    #
    # def __configure_injector(self):
    #     if len(self.__inj_models):
    #         self.__injection_model = InjectionModel(self.__name, self,
    #                                                       self.istrategy,
    #                                                       self.__uid,
    #                                                       self.__injection_iids,
    #                                                       self.__children_uids)
    #
    #         self.__transform_strategy.create(self.__injectParams)
    #
    # def __configure_debug(self):
    #     # TODO - fix dstrategy registration
    #     if self.dstrategy:
    #         loader = ModuleLoader()
    #         self.__debug_strategy = loader.load(self.dstrategy)
    #         self.__debug_strategy.create(self.debugParams)
    #         self.__transform_engine.registerDebugStrategy(self.__debug_strategy)
    #
    def __applyModel(self, timeout):
        pending = 0
        err = 0
        for seg in self.__model_children:
            r = seg.apply(timeout)
            if r == 1:
                pending += 1
            elif r == -1:
                err += 1
        if self.__transform_strategy is not None:
            r = self.__transform_strategy.apply(timeout)
            if r == 1:
                pending += 1
            elif r == -1:
                err += 1
        else:
            self.logger.debug("TransformEngine.__applyModel(): self.__transform_strategy is not defined for ({:s}).\n".format(self.name))
        if err:
            return -1
        elif pending:
            return 1
        else:
            return 0

    def __applyInjection(self, timeout):
        pending = 0
        err = 0
        for seg in self.__injection_children:
            r = seg.apply(timeout)
            if r == 1:
                pending += 1
            elif r == -1:
                err += 1
        if self.__injection_strategy is not None:
            r = self.__injection_strategy.apply(timeout)
            if r == 1:
                pending += 1
            elif r == -1:
                err += 1
        else:
            self.logger.debug("TransformEngine.__applyInjection(): self.__injection_strategy is not defined for ({:s}).\n".format(self.name))
        if err:
            return -1
        elif pending:
            return 1
        else:
            return 0

    @property
    def uid(self):
        return self.__uid

    # @uid.setter
    # def uid(self, uid):
    #     if not isinstance(uid, int):
    #         raise ModelError("uid is not of type int.")
    #     self.__uid = uid

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def tstrategy(self):
        return self.__tstrategy

    @tstrategy.setter
    def tstrategy(self, tstrategy):
        self.__tstrategy = tstrategy

    @property
    def inj_models(self):
        return self.__inj_models

    @inj_models.setter
    def inj_models(self, inj_models):
        self.__inj_models = inj_models

    @property
    def istrategy(self):
        return self.__istrategy

    @istrategy.setter
    def istrategy(self, istrategy):
        self.__istrategy = istrategy

    @property
    def dstrategy(self):
        return self.__dstrategy

    @dstrategy.setter
    def dstrategy(self, dstrategy):
        self.__dstrategy = dstrategy

    @property
    def cstrategy(self):
        return self.__cstrategy

    @cstrategy.setter
    def cstrategy(self, cstrategy):
        self.__cstrategy = cstrategy

    @property
    def transformParams(self):
        return self.__transformParams

    @transformParams.setter
    def transformParams(self, transformParams):
        self.__transformParams = transformParams

    @property
    def injectParams(self):
        return self.__injectParams

    @injectParams.setter
    def injectParams(self, injectParams):
        self.__injectParams = injectParams

    @property
    def debugParams(self):
        return self.__debugParams

    @debugParams.setter
    def debugParams(self, debugParams):
        self.__debugParams = debugParams

    @property
    def inodeParams(self):
        return self.__inodeParams

    @inodeParams.setter
    def inodeParams(self, inodeParams):
        self.__inodeParams = inodeParams

    def get_data_value(self):
        return self.data_value

    def indent(self):
        TransformEngine.__indent += 4

    def dedent(self):
        TransformEngine.__indent -= 4

    def writeln(self, ln):
        print(" " * self.__indent, ln)

    def dump(self, indent):
        TransformEngine.__indent = indent
        for injector in self.__injection_children:
            injector.dump(TransformEngine.__indent)
        for children in self.__model_children:
            children.dump()
        if self.__transform_strategy:
            self.__transform_strategy.dump(TransformEngine.__indent)
        if self.__injection_strategy:
            self.__injection_strategy.dump(TransformEngine.__indent)
        if self.__debug_strategy:
            self.__debug_strategy.dump(TransformEngine.__indent)
        if self._client_interface:
            self._client_interface.dump(TransformEngine.__indent)
        if self._host_interface:
            self._host_interface.dump(TransformEngine.__indent)
        if self._testinjection_interface:
            self._testinjection_interface.dump(TransformEngine.__indent)
