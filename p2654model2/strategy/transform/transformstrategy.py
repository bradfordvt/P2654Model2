#!/usr/bin/env python
"""
    Wrapper class for accessing transform strategies plugin modules.
    Copyright (C) 2021  Bradford G. Van Treuren

    Wrapper class for accessing transform strategies plugin modules.

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

module_logger = logging.getLogger('p2654model2.strategy.transforms.transformstrategy')


@logged
@traced
class TransformStrategy(object):
    __indent = 0

    def __init__(self, name):
        self.logger = logging.getLogger('p2654model2.strategy.transforms.transformstrategy')
        self.logger.info('Creating an instance of TransformStrategy({:s})'.format(name))
        self.name = name
        self.child_uids = None
        self.child_names = None
        self.node_uid = None
        self.tstrategy = None
        self.module = None
        self.parameters = None
        self.class_obj = None
        self.selector = None
        self.derivations = None
        self.control = None

    def create(self, params):
        self.parameters = params
        ml = ModuleLoader.get_moduleloader()
        self.module = ml.load(self.tstrategy, self.tstrategy)
        if self.module is None:
            self.module = ml.load("transformwrap", self.tstrategy)
        if self.module is None:
            raise AssertionError("Class {:s} could not be found in any modules.".format(self.tstrategy))
        # print("module.__dict__ = ", self.module.__dict__)
        cls = getattr(self.module, self.tstrategy)
        self.class_obj = cls()
        self.class_obj.set_sendRequestCallback(self.sendRequest)
        self.class_obj.set_sendResponseCallback(self.sendResponse)
        self.class_obj.set_updateDataValueCallback(self.updateDataValue)
        self.class_obj.set_sendObserverCallback(self.sendObserver)
        self.class_obj.set_registerObserverCallback(self.register_observer)
        ret = self.class_obj.create(self.name, self.node_uid, self.child_uids, self.child_names, params)
        return ret

    def configure(self):
        return self.class_obj.configure()

    def handleRequest(self, message):
        self.logger.debug("TransformStrategy.handleRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return self.class_obj.handleRequest(self.node_uid, message)

    def handleResponse(self, message):
        self.logger.debug("TransformStrategy.handleResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return self.class_obj.handleResponse(self.node_uid, message)

    def updateRequest(self, message):
        self.logger.debug("TransformStrategy.updateRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return self.class_obj.updateRequest(self.node_uid, message)

    def updateResponse(self, message):
        self.logger.debug("TransformStrategy.updateResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return self.class_obj.updateResponse(self.node_uid, message)

    def getStatus(self, timeout=0):
        return self.class_obj.getStatus(self.node_uid, timeout)

    def getError(self, timeout=0):
        return self.class_obj.getError(self.node_uid, timeout)

    def apply(self, timeout=0):
        self.logger.debug("TransformStrategy.apply({:s}): processing\n".format(self.name))
        return self.class_obj.apply(self.node_uid, timeout)

    def getCallbackNames(self):
        return self.class_obj.getCallbackNames()

    def destroy(self):
        return self.class_obj.destroy(self.node_uid)

    ########### To support builders
    def register_node_uid(self, node_uid):
        self.node_uid = node_uid

    def register_tstrategy(self, tstrategy):
        self.tstrategy = tstrategy

    def register_child_uids(self, child_uids):
        self.child_uids = child_uids

    def register_child_names(self, child_names):
        self.child_names = child_names

    @staticmethod
    def register_observer(node_uid, control_list):
        nc = NodeContainer.get_nodecontainer()
        for control in control_list:
            node = nc.get_node_by_path(control)
            te = node.transform_engine
            te.register_observer(node_uid)

    @staticmethod
    def sendObserver(node_uid, msg):
        nc = NodeContainer.get_nodecontainer()
        node = nc.get_node_by_id(node_uid)
        te = node.transform_engine
        return te.update_observer(msg)

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
    def updateDataValue(node_uid, msg):
        nc = NodeContainer.get_nodecontainer()
        node = nc.get_node_by_id(node_uid)
        te = node.transform_engine
        return te.updateDataValue(msg)

    def update_observer(self, message):
        self.logger.debug("TransformStrategy.update_observer({:s})\n".format(self.name))
        return self.class_obj.update_observer(self.node_uid, message)

    def indent(self):
        TransformStrategy.__indent += 4

    def dedent(self):
        TransformStrategy.__indent -= 4

    def writeln(self, ln):
        print(" " * TransformStrategy.__indent, ln)

    def dump(self, indent):
        TransformStrategy.__indent = indent
        self.writeln("Dumping TransformStrategy: {:s}".format(str(self.name)))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("tstrategy = {:s}".format(str(self.tstrategy)))
        self.writeln("parameters = {:s}".format(str(self.parameters)))
        self.writeln("child_uids = {:s}".format(str(self.child_uids)))
        self.writeln("module = {:s}".format(str(self.module)))
        self.writeln("class_obj = {:s}".format(str(self.class_obj)))
        self.class_obj.dump(TransformStrategy.__indent)
        self.dedent()


# class TransformRequestCallback(p2654callback.P2654Callback):
#     def __init__(self):
#         p2654callback.P2654Callback.__init__(self)
#
#     def send(self, node_uid, msg):
#         nc = NodeContainer.get_nodecontainer()
#         node = nc.get_node_by_id(node_uid)
#         te = node.transform_engine
#         return te.sendRequest(msg)
#
#
# class TransformResponseCallback(p2654callback.P2654Callback):
#     def __init__(self):
#         p2654callback.P2654Callback.__init__(self)
#
#     def send(self, node_uid, msg):
#         nc = NodeContainer.get_nodecontainer()
#         node = nc.get_node_by_id(node_uid)
#         te = node.transform_engine
#         return te.sendResponse(msg)
