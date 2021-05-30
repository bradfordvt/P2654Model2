#!/usr/bin/env python
"""
    Specialized Transformation Strategy for GPIO REGISTERs.
    Copyright (C) 2021  Bradford G. Van Treuren

    Specialized Transformation Strategy for GPIO REGISTERs.
    This strategy is implemented as a built-in plug-in module wrapped by its own TransformationStrategy
    instance.  To use this strategy, specify the name GPIOTransform as the "tstrategy"
    field of the building block.

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
__date__ = "2021/03/05"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


import p2654model2.rvf.protocols.GPIO_pb2
import p2654model2.rvf.rvfmessage_pb2


import logging
from autologging import traced, logged


module_logger = logging.getLogger('p2654model2.strategy.transforms.strategies.GPIOTransform')


@logged
@traced
class GPIOTransform(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('p2654model2.strategy.transforms.strategies.GPIOTransform')
        self.logger.info('Creating an instance of GPIOTransform')
        self.name = None
        self.node_uid = None
        self.child_uid = None
        self.children_uids = None
        self.children_names = None
        self.params = None
        self.command = None
        self.sendRequestCallback = None
        self.sendResponseCallback = None
        self.updateDataValueCallback = None
        self.registerObserverCallback = None
        self.sendObserverCallback = None
        # self.reqQ = []
        # self.respQ = []
        self.input = []
        self.output = []

    def create(self, name, node_uid, children_uids, children_names, params):
        # print("GPIOTransform params = {:s}".format(params))
        self.name = name
        self.node_uid = node_uid
        self.children_uids = children_uids
        self.children_names = children_names
        self.params = params
        return None

    def configure(self):
        return True

    def handleRequest(self, node_uid, message):
        self.logger.debug("GPIOTransform.handleRequest(): processing {:s} RVF\n".format(message.metaname))
        # print("GPIOTransform handling request ({:s}).".format(message.metaname))
        raise AssertionError("handleRequest called for leaf GPIOTransform.")

    def handleResponse(self, node_uid, message):
        self.logger.debug("GPIOTransform.handleResponse(): processing {:s} RVF\n".format(message.metaname))
        # print("GPIOTransform handling response ({:s}).".format(message.metaname))
        raise AssertionError("handleResponse called for leaf GPIOTransform.")

    def updateRequest(self, node_uid, message):
        self.logger.debug("GPIOTransform.updateRequest(): processing {:s} RVF\n".format(message.metaname))
        if message.metaname == "INPUT":
            s = p2654model2.rvf.protocols.GPIO_pb2.INPUT()
            s.ParseFromString(message.serialized)
            return self.__input_cb(node_uid, s)
        elif message.metaname == "OUTPUT":
            s = p2654model2.rvf.protocols.GPIO_pb2.OUTPUT()
            s.ParseFromString(message.serialized)
            return self.__output_cb(node_uid, s)
        return 0

    def updateResponse(self, node_uid, message):
        self.logger.debug("GPIOTransform.updateResponse(): processing {:s} RVF\n".format(message.metaname))
        if message.metaname == "INPUT":
            s = p2654model2.rvf.protocols.GPIO_pb2.INPUT()
            s.ParseFromString(message.serialized)
            return self.__input_resp_cb(node_uid, s)
        elif message.metaname == "OUTPUT":
            s = p2654model2.rvf.protocols.GPIO_pb2.OUTPUT()
            s.ParseFromString(message.serialized)
            return self.__output_resp_cb(node_uid, s)
        return 0

    def getStatus(self, node_uid, timeout):
        print("GPIOTransform getStatus ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.STATUS
        rvf.message = "OK"
        rvf.code = 0
        return rvf

    def getError(self, node_uid, timeout):
        print("GPIOTransform getError ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFError()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.ERROR
        rvf.message = "UNKNOWN"
        rvf.code = 0
        return rvf

    def apply(self, node_uid, timeout=0):
        self.logger.debug("GPIOTransform.apply(): processing {:d} node_uid\n".format(node_uid))
        print("GPIOTransform apply()")
        return 0

    def getCallbackNames(self):
        return ["INPUT", "OUTPUT"]

    def destroy(self, node_uid):
        return None

    def __input_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.input = message.value
        self.__updateDataValue(node_uid, message)
        return True

    def __output_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.output = message.value
        return True

    def __input_resp_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.input = message.value
        self.__updateDataValue(node_uid, message)
        return True

    def __output_resp_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.output = message.value
        return True

    def __sendRequest(self, node_uid, message, metaname):
        self.logger.debug("GPIOTransform.__sendRequest(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = self.node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendRequestCallback(node_uid, wrapper)

    def __sendResponse(self, node_uid, message, metaname, uid):
        self.logger.debug("GPIOTransform.__sendResponse(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendResponseCallback(node_uid, wrapper)

    def __updateDataValue(self, node_uid, message):
        self.logger.debug("GPIOTransform.__updateDataValue({:s}):\n".format(self.name))
        dvmsg = p2654model2.rvf.rvfmessage_pb2.RVFDataValue()
        dvmsg.UID = node_uid
        dvmsg.nrbits = message.nrbits
        dvmsg.data.append(self.input)
        return self.updateDataValueCallback(node_uid, dvmsg)

    def set_sendRequestCallback(self, callback):
        self.sendRequestCallback = callback

    def set_sendResponseCallback(self, callback):
        self.sendResponseCallback = callback

    def set_updateDataValueCallback(self, callback):
        self.updateDataValueCallback = callback

    def set_registerObserverCallback(self, callback):
        self.registerObserverCallback = callback

    def set_sendObserverCallback(self, callback):
        self.sendObserverCallback = callback

    def indent(self):
        self.__indent += 4

    def dedent(self):
        self.__indent -= 4

    def writeln(self, ln):
        print(" " * self.__indent, ln)

    def dump(self, indent):
        self.__indent = indent
        self.writeln("Dumping TDRTransform: {:s}".format(str(self.name)))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        if self.child_uid:
            self.writeln("child_uid = {:d}".format(self.child_uid))
        else:
            self.writeln("child_uid = {:s}".format(str(self.child_uid)))
        self.writeln("params = {:s}".format(str(self.params)))
        self.writeln("children_uids = {:s}".format(str(self.children_uids)))
        self.writeln("command = {:s}".format(str(self.command)))
        self.dedent()
