#!/usr/bin/env python
"""
    Wrapper class for accessing injection strategies plugin modules.
    Copyright (C) 2021  Bradford G. Van Treuren

    Wrapper class for accessing injection strategies plugin modules.

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


from p2654model2.builder.moduleloader import ModuleLoader
from p2654model2.builder.nodecontainer import NodeContainer


import logging
from autologging import traced, logged


module_logger = logging.getLogger('p2654model2.strategy.inject.injectionstrategy')


@logged
@traced
class InjectionStrategy(object):
    global_iid = 0
    __indent = 0

    def __init__(self, name):
        self.logger = logging.getLogger('p2654model2.strategy.inject.injectionstrategy')
        self.logger.info('Creating an instance of InjectionStrategy({:s})'.format(name))
        self.name = name
        self.istrategy = None
        self.inj_iids = self.global_iid
        self.global_iid += 1
        self.children_uids = []
        self.node_uid = None
        self.module = None
        self.parameters = None
        self.class_obj = None

    def create(self, params):
        self.parameters = params
        ml = ModuleLoader.get_moduleloader()
        self.module = ml.load(self.istrategy, self.istrategy)
        if self.module is None:
            self.module = ml.load("injectwrap", self.istrategy)
        if self.module is None:
            raise AssertionError("Class {:s} could not be found in any modules.".format(self.istrategy))
        cls = getattr(self.module, self.istrategy)
        self.class_obj = cls()
        ret = self.class_obj.create(self.name, self.node_uid,  self.inj_iids, self.children_uids, params)
        self.class_obj.set_sendRequestCallback(self.sendRequest)
        self.class_obj.set_sendResponseCallback(self.sendResponse)
        self.class_obj.set_updateRequestCallback(self.updateRequest)
        self.class_obj.set_updateResponseCallback(self.updateResponse)
        return ret

    def handleRequest(self, message):
        self.logger.debug("InjectionStrategy.handleRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return self.class_obj.handleRequest(self.node_uid, message)

    def handleResponse(self, message):
        self.logger.debug("InjectionStrategy.handleResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return self.class_obj.handleResponse(self.node_uid, message)

    def getStatus(self, timeout=0):
        return self.class_obj.getStatus(self.node_uid, timeout)

    def getError(self, timeout=0):
        return self.class_obj.getError(self.node_uid, timeout)

    def apply(self, timeout=0):
        self.logger.debug("InjectionStrategy.apply({:s}): processing\n".format(self.name))
        return self.class_obj.apply(self.node_uid, timeout)

    def getCallbackNames(self):
        return self.class_obj.getCallbackNames()

    def destroy(self):
        return self.class_obj.destroy(self.node_uid)

    ########### To support builders
    def register_node_uid(self, node_uid):
        self.node_uid = node_uid

    def register_istrategy(self, istrategy):
        self.istrategy = istrategy

    def register_child_uids(self, child_uids):
        self.child_uids = child_uids

    @staticmethod
    def sendRequest(node_uid, msg):
        nc = NodeContainer.get_nodecontainer()
        node = nc.get_node_by_id(node_uid)
        te = node.transform_engine
        return te.sendRequest(msg)

    @staticmethod
    def sendResponse(node_uid, msg):
        nc = NodeContainer.get_nodecontainer()
        node = nc.get_node_by_id(node_uid)
        te = node.transform_engine
        return te.sendResponse(msg)

    @staticmethod
    def updateRequest(node_uid, msg):
        nc = NodeContainer.get_nodecontainer()
        node = nc.get_node_by_id(node_uid)
        te = node.transform_engine
        return te.updateRequest(msg)

    @staticmethod
    def updateResponse(node_uid, msg):
        nc = NodeContainer.get_nodecontainer()
        node = nc.get_node_by_id(node_uid)
        te = node.transform_engine
        return te.updateResponse(msg)

    def indent(self):
        self.__indent += 4

    def dedent(self):
        self.__indent -= 4

    def writeln(self, ln):
        print("" * self.__indent, ln)

    def dump(self, indent):
        self.__indent = indent
        self.writeln("Dumping InjectionStrategy: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("istrategy = {:s}".format(self.istrategy))
        self.writeln("parameters = {:s}".format(self.parameters))
        self.writeln("children_uids = {:s}".format(str(self.children_uids)))
        self.writeln("module = {:s}".format(str(self.module)))
        self.writeln("class_obj = {:s}".format(str(self.class_obj)))
        self.class_obj.dump(self.__indent)
        self.dedent()
