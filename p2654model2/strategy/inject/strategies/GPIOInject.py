#!/usr/bin/env python
"""
    Specialized Injection Strategy for GPIO registers.
    Copyright (C) 2021  Bradford G. Van Treuren

    Specialized Injection Strategy for GPIO registers.  This strategy is implemented as
    a built-in plug-in module wrapped by its own InjectionStrategy instance.  To use
    this strategy, specify the name GPIOInject as the "istrategy" field of the building block.

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
__date__ = "2021/03/10"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


import p2654model2.rvf.protocols.GPIO_pb2
import p2654model2.rvf.rvfmessage_pb2
from p2654model2.error.ModelError import ModelError
from queue import Queue

import logging
from autologging import traced, logged

module_logger = logging.getLogger('p2654model2.strategy.inject.strategies.GPIOInject')


@logged
@traced
class GPIOInject(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('p2654model2.strategy.inject.strategies.GPIOInject')
        self.logger.info('Creating an instance of GPIOInject')
        self.name = None
        self.node_uid = None
        self.command = None
        self.inject_iids = None
        self.children_uids = []
        self.child_uid = -1
        self.params = None
        self.sendRequestCallback = None
        self.sendResponseCallback = None
        self.updateRequestCallback = None
        self.updateResponseCallback = None
        # self.reqQ = []
        # self.respQ = []
        # self.updateReqQ = []
        # self.updateRespQ = []
        self.reqQ = Queue(maxsize=0)
        self.respQ = Queue(maxsize=0)
        self.updateReqQ = Queue(maxsize=0)
        self.updateRespQ = Queue(maxsize=0)

    def create(self, name, node_uid, inject_iids, children_uids, params):
        print("GPIOInject params = {:s}".format(params))
        self.name = name
        self.node_uid = node_uid
        self.inject_iids = inject_iids
        self.children_uids = children_uids
        self.params = params
        return None

    def handleRequest(self, node_uid, message):
        self.logger.debug("GPIOInject.handleRequest(): processing {:s} RVF\n".format(message.metaname))
        print("GPIOInject handling request ({:s}).".format(message.metaname))
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
        self.logger.debug("GPIOInject.handleResponse(): processing {:s} RVF\n".format(message.metaname))
        print("GPIOInject handling response ({:s}).".format(message.metaname))
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
        print("GPIOInject getStatus ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.STATUS
        rvf.message = "OK"
        rvf.code = 0
        return rvf

    def getError(self, node_uid, timeout):
        print("GPIOInject getError ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFError()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.ERROR
        rvf.message = "UNKNOWN"
        rvf.code = 0
        return rvf

    def apply(self, node_uid, timeout=0):
        self.logger.debug("GPIOInject.apply(): processing {:d} node_uid\n".format(node_uid))
        return 0

    def getCallbackNames(self):
        return ["INPUT", "OUTPUT"]

    def destroy(self, node_uid):
        return None

    def __input_cb(self, node_uid, message):
        errcnt = 0
        self.child_uid = message.UID
        self.command = "INPUT"
        ## self.reqQ.append((node_uid, message, "INPUT"))
        # self.reqQ.put((node_uid, message, "INPUT"))
        ret = self.__sendRequest(node_uid, message, "INPUT")
        if ret is None:
            errcnt += 1
        # Singleton.increment_pending()
        metaname = "INPUT"
        rvf1 = p2654model2.rvf.protocols.GPIO_pb2.INPUT()
        rvf1.UID = self.child_uid
        rvf1.value = message.value
        ## self.updateReqQ.append((rvf1.UID, rvf1, "INPUT"))
        # self.updateReqQ.put((rvf1.UID, rvf1, "INPUT"))
        ret = self.__updateRequest(node_uid, message, "INPUT")
        if ret is None:
            errcnt += 1
        # Singleton.increment_pending()
        # return True
        return False if errcnt else True

    def __output_cb(self, node_uid, message):
        errcnt = 0
        self.child_uid = message.UID
        self.command = "OUTPUT"
        ## self.reqQ.append((node_uid, message, "OUTPUT"))
        # self.reqQ.put((node_uid, message, "OUTPUT"))
        ret = self.__sendRequest(node_uid, message, "OUTPUT")
        if ret is None:
            errcnt += 1
        # Singleton.increment_pending()
        metaname = "OUTPUT"
        # rvf1 = p2654model2.rvf.protocols.GPIO_pb2.OUTPUT()
        # rvf1.UID = self.child_uid
        # rvf1.value = message.value
        # # self.updateReqQ.append((rvf1.UID, rvf1, "OUTPUT"))
        # self.updateReqQ.put((rvf1.UID, rvf1, "OUTPUT"))
        # ret = self.__updateRequest(node_uid, message, "INPUT")
        # if ret is None:
        #     errcnt += 1
        # Singleton.increment_pending()
        # return True
        return False if errcnt else True

    def __input_resp_cb(self, node_uid, message):
        if self.command != "INPUT":
            raise ModelError("Invalid response sent.")
        ## self.respQ.append((node_uid, message, "INPUT", self.child_uid))
        ## self.updateRespQ.append((node_uid, message, "INPUT", self.child_uid))
        # self.updateRespQ.put((node_uid, message, "INPUT", self.child_uid))
        ret = self.__updateRequest(node_uid, message, "INPUT")
        if ret is None:
            return False
        # Singleton.decrement_pending()
        return True

    def __output_resp_cb(self, node_uid, message):
        if self.command != "OUTPUT":
            raise ModelError("Invalid response sent.")
        ## self.respQ.append((node_uid, message, "OUTPUT", self.child_uid))
        ## self.updateRespQ.append((node_uid, message, "OUTPUT", self.child_uid))
        # self.updateRespQ.put((node_uid, message, "OUTPUT", self.child_uid))
        ret = self.__updateResponse(node_uid, message, "OUTPUT", self.child_uid)
        if ret is None:
            return False
        # Singleton.decrement_pending()
        return True

    def __sendRequest(self, node_uid, message, metaname):
        self.logger.debug("GPIOInject.__sendRequest(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = self.node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendRequestCallback(node_uid, wrapper)

    def __sendResponse(self, node_uid, message, metaname, uid):
        self.logger.debug("GPIOInject.__sendResponse(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = self.command
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendResponseCallback(node_uid, wrapper)

    def __updateRequest(self, node_uid, message, metaname):
        self.logger.debug("GPIOInject.__updateRequest(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.updateRequestCallback(node_uid, wrapper)

    def __updateResponse(self, node_uid, message, metaname, uid):
        self.logger.debug("GPIOInject.__updateResponse(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.updateResponseCallback(node_uid, wrapper)

    def set_sendRequestCallback(self, callback):
        self.sendRequestCallback = callback

    def set_sendResponseCallback(self, callback):
        self.sendResponseCallback = callback

    def set_updateRequestCallback(self, callback):
        self.updateRequestCallback = callback

    def set_updateResponseCallback(self, callback):
        self.updateResponseCallback = callback

    def indent(self):
        self.__indent += 4

    def dedent(self):
        self.__indent -= 4

    def writeln(self, ln):
        print("" * self.__indent, ln)

    def dump(self, indent):
        self.__indent = indent
        self.writeln("Dumping GPIOInject: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("child_uid = {:d}".format(self.child_uid))
        self.writeln("params = {:s}".format(self.params))
        self.writeln("children_uids = {:s}".format(str(self.children_uids)))
        self.writeln("command = {:s}".format(str(self.command)))
        self.dedent()
