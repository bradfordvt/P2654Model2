#!/usr/bin/env python
"""
    Specialized Transformation Strategy for GPIO CONTROLLERs in the P2654Simulations tester.
    Copyright (C) 2021  Bradford G. Van Treuren

    Specialized Transformation Strategy for GPIO CONTROLLERs in the P2654Simulations tester.
    This strategy is implemented as a built-in plug-in module wrapped by its own TransformationStrategy
    instance.  To use this strategy, specify the name GPIOControllerAssembly as the "tstrategy"
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


import logging
from autologging import traced, logged
import p2654model2.rvf.protocols.GPIO_pb2
import p2654model2.rvf.rvfmessage_pb2
from p2654model2.builder.drivers import Drivers

# create logger
module_logger = logging.getLogger('p2654model2.strategy.transform.strategies.GPIOControllerAssembly')


@logged
@traced
class GPIOControllerAssembly(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('P2654Model.transform.strategies.GPIOControllerAssembly')
        self.logger.info('Creating an instance of GPIOControllerAssembly')
        self.name = None
        self.node_uid = None
        self.child_uid = None
        self.children_uids = None
        self.children_names = None
        self.params = None
        self.command = None
        self.sendRequestCallback = None
        self.sendResponseCallback = None
        self.updateRequestCallback = None
        self.updateResponseCallback = None
        self.updateDataValueCallback = None
        self.registerObserverCallback = None
        self.sendObserverCallback = None
        self.input = None
        self.output = None
        self.update = None
        self.pending = None
        self.capture = None
        self.gpio_controller = Drivers.get_gpio()

    def create(self, name, node_uid, children_uids, children_names, params):
        # print("GPIOControllerAssembly params = {:s}".format(str(params)))
        self.name = name
        self.node_uid = node_uid
        self.children_uids = children_uids
        self.children_names = children_names
        self.params = params
        return None

    def configure(self):
        return True

    def handleRequest(self, node_uid, message):
        self.logger.debug("GPIOControllerAssembly.handleRequest(): processing {:s} RVF\n".format(message.metaname))
        print("GPIOControllerAssembly handling request ({:s}).".format(message.metaname))
        if message.metaname == "INPUT":
            s = p2654model2.rvf.protocols.GPIO_pb2.INPUT()
            s.ParseFromString(message.serialized)
            return self.__input_cb(node_uid, s)
        elif message.metaname == "OUTPUT":
            s = p2654model2.rvf.protocols.GPIO_pb2.OUTPUT()
            s.ParseFromString(message.serialized)
            return self.__output_cb(node_uid, s)
        return None

    def handleResponse(self, node_uid, message):
        self.logger.debug("GPIOControllerAssembly.handleResponse(): processing {:s} RVF\n".format(message.metaname))
        print("GPIOControllerAssembly handling response ({:s}).".format(message.metaname))
        if message.metaname == "INPUT":
            s = p2654model2.rvf.protocols.GPIO_pb2.INPUT()
            s.ParseFromString(message.serialized)
            return self.__input_resp_cb(node_uid, s)
        elif message.metaname == "OUTPUT":
            s = p2654model2.rvf.protocols.GPIO_pb2.OUTPUT()
            s.ParseFromString(message.serialized)
            return self.__output_resp_cb(node_uid, s)
        return None

    def getStatus(self, node_uid, timeout):
        print("GPIOControllerAssembly getStatus ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.STATUS
        rvf.message = "OK"
        rvf.code = 0
        return rvf

    def getError(self, node_uid, timeout):
        print("GPIOControllerAssembly getError ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFError()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.ERROR
        rvf.message = "UNKNOWN"
        rvf.code = 0
        return rvf

    def apply(self, node_uid, timeout=0):
        self.logger.debug("GPIOControllerAssembly.apply(): processing {:d} node_uid\n".format(node_uid))
        print("GPIOControllerAssembly apply()")
        pending = 0
        err = 0
        if self.pending:
            if self.capture:
                self.gpio_controller.read()
                wrvf = p2654model2.rvf.protocols.GPIO_pb2.INPUT()
                wrvf.UID = node_uid
                wrvf.value = self.gpio_controller.get_value()
                pending += 1
                ret = self.__sendResponse(node_uid, wrvf, "INPUT", self.child_uid)
                if not ret:
                    err += 1
                self.pending = False
                self.capture = False
            if self.update:
                wrvf = p2654model2.rvf.protocols.GPIO_pb2.OUTPUT()
                wrvf.UID = node_uid
                ret = self.gpio_controller.write(self.output)
                if not ret:
                    err += 1
                pending += 1
                ret = self.__sendResponse(node_uid, wrvf, "OUTPUT", self.child_uid)
                if not ret:
                    err += 1
                self.update = False
        self.pending = False
        if err:
            return -1
        elif pending:
            return 1
        else:
            return 0

    def getCallbackNames(self):
        return ["INPUT", "OUTPUT"]

    def destroy(self, node_uid):
        return None

    def get_size(self):
        return self.nrbits

    def __input_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.input = message.value
        self.pending = True
        self.capture = True
        return True

    def __output_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.output = message.value
        self.pending = True
        self.update = True
        return True

    def __input_resp_cb(self, node_uid, message):
        self.input = message.value
        self.__updateDataValue(node_uid, message)
        return True

    def __output_resp_cb(self, node_uid, message):
        return True

    def __sendResponse(self, node_uid, message, metaname, uid):
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendResponseCallback(node_uid, wrapper)

    def __updateDataValue(self, node_uid, message):
        self.logger.debug("GPIOControllerAssembly.__updateDataValue({:s}):\n".format(self.name))
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
        self.writeln("Dumping GPIOControllerAssembly: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("child_uid = {:s}".format(str(self.child_uid)))
        self.writeln("params = {:s}".format(str(self.params)))
        self.writeln("children_uids = {:s}".format(str(self.children_uids)))
        self.dedent()
