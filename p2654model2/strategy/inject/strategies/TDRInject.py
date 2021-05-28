#!/usr/bin/env python
"""
    Specialized Injection Strategy for TDR registers.
    Copyright (C) 2021  Bradford G. Van Treuren

    Specialized Injection Strategy for TDR registers.  This strategy is implemented as
    a built-in plug-in module wrapped by its own InjectionStrategy instance.  To use
    this strategy, specify the name TDRInject as the "istrategy" field of the building block.

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


import p2654model2.rvf.protocols.SCAN_pb2
import p2654model2.rvf.rvfmessage_pb2
from p2654model2.error.ModelError import ModelError
from threading import Lock, Condition
from queue import Queue

import logging
from autologging import traced, logged

module_logger = logging.getLogger('p2654model2.strategy.inject.strategies.TDRInject')


@logged
@traced
class TDRInject(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('p2654model2.strategy.inject.strategies.TDRInject')
        self.logger.info('Creating an instance of TDRInject')
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
        self.reqQ = Queue(maxsize=0)
        self.respQ = Queue(maxsize=0)
        self.updateReqQ = Queue(maxsize=0)
        self.updateRespQ = Queue(maxsize=0)
        # mutex to regulate the access to the response_received_cv variable
        self.response_mutex = Lock()
        # condition variable: notifies the host callback that the
        # thread related to a client response has finished the request
        self.response_cv = Condition(self.response_mutex)
        # variable coupled to response_cv to avoid spurious wakeups
        self.response_v = 0
        self.response = None

        self.local_access_mutex = Lock()

    def create(self, name, node_uid, inject_iids, children_uids, params):
        print("TDRInject params = {:s}".format(params))
        self.name = name
        self.node_uid = node_uid
        self.inject_iids = inject_iids
        self.children_uids = children_uids
        self.params = params
        return None

    def handleRequest(self, node_uid, message):
        self.logger.debug("TDRInject.handleRequest(): processing {:s} RVF\n".format(message.metaname))
        print("TDRInject handling request ({:s}).".format(message.metaname))
        if message.metaname == "CSU":
            s = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            s.ParseFromString(message.serialized)
            return self.__csu_cb(node_uid, s)
        elif message.metaname == "SU":
            s = p2654model2.rvf.protocols.SCAN_pb2.SU()
            s.ParseFromString(message.serialized)
            return self.__su_cb(node_uid, s)
        elif message.metaname == "CS":
            s = p2654model2.rvf.protocols.SCAN_pb2.CS()
            s.ParseFromString(message.serialized)
            return self.__cs_cb(node_uid, s)
        elif message.metaname == "S":
            s = p2654model2.rvf.protocols.SCAN_pb2.S()
            s.ParseFromString(message.serialized)
            return self.__s_cb(node_uid, s)
        elif message.metaname == "ENDSTATE":
            s = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
            s.ParseFromString(message.serialized)
            return self.__endstate_cb(node_uid, s)
        return None

    def handleResponse(self, node_uid, message):
        self.logger.debug("TDRInject.handleResponse(): processing {:s} RVF\n".format(message.metaname))
        print("TDRInject handling response ({:s}).".format(message.metaname))
        if message.metaname == "CSU":
            s = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            s.ParseFromString(message.serialized)
            return self.__csu_resp_cb(node_uid, s)
        elif message.metaname == "SU":
            s = p2654model2.rvf.protocols.SCAN_pb2.SU()
            s.ParseFromString(message.serialized)
            return self.__su_resp_cb(node_uid, s)
        elif message.metaname == "CS":
            s = p2654model2.rvf.protocols.SCAN_pb2.CS()
            s.ParseFromString(message.serialized)
            return self.__cs_resp_cb(node_uid, s)
        if message.metaname == "S":
            s = p2654model2.rvf.protocols.SCAN_pb2.S()
            s.ParseFromString(message.serialized)
            return self.__s_resp_cb(node_uid, s)
        elif message.metaname == "ENDSTATE":
            s = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
            s.ParseFromString(message.serialized)
            return self.__endstate_resp_cb(node_uid, s)
        return None

    def getStatus(self, node_uid, timeout):
        print("TDRInject getStatus ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.STATUS
        rvf.message = "OK"
        rvf.code = 0
        return rvf

    def getError(self, node_uid, timeout):
        print("TDRInject getError ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFError()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.ERROR
        rvf.message = "UNKNOWN"
        rvf.code = 0
        return rvf

    def apply(self, node_uid, timeout=0):
        self.logger.debug("TDRInject.apply(): processing {:d} node_uid\n".format(node_uid))
        print("TDRInject apply()")
        pending = 0
        err = 0
        # self.local_access_mutex.acquire()
        if not self.reqQ.empty():
            m = self.reqQ.get(block=True, timeout=None)
            pending += 1
            ret = self.__sendRequest(m[0], m[1], m[2])
            if not ret:
                err += 1
        if not self.respQ.empty():
            r = self.respQ.get(block=True, timeout=None)
            pending += 1
            ret = self.__sendResponse(r[0], r[1], r[2], r[3])
            if not ret:
                err += 1
        if not self.updateReqQ.empty():
            m = self.updateReqQ.get(block=True, timeout=None)
            pending += 1
            ret = self.__updateRequest(m[0], m[1], m[2])
            if not ret:
                err += 1
        if not self.updateRespQ.empty():
            r = self.updateRespQ.get(block=True, timeout=None)
            pending += 1
            ret = self.__updateResponse(r[0], r[1], r[2], r[3])
            if not ret:
                err += 1
        if err:
            return -1
        elif pending:
            return 1
        else:
            return 0

    def getCallbackNames(self):
        return ["CSU", "SU", "CS", "S", "ENDSTATE"]

    def destroy(self, node_uid):
        return None

    def __csu_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.command = "CSU"
        self.reqQ.put((node_uid, message, "CSU"))
        metaname = "CSU"
        rvf1 = p2654model2.rvf.protocols.SCAN_pb2.CSU()
        rvf1.UID = self.child_uid
        rvf1.nrbits = message.nrbits
        for v in message.si_vector:
            rvf1.si_vector.append(v)
        for v in message.so_vector:
            rvf1.so_vector.append(v)
        self.updateReqQ.put((rvf1.UID, rvf1, "CSU"))
        return True

    def __su_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.command = "SU"
        self.reqQ.put((node_uid, message, "SU"))
        metaname = "SU"
        rvf1 = p2654model2.rvf.protocols.SCAN_pb2.SU()
        rvf1.UID = self.child_uid
        rvf1.nrbits = message.nrbits
        for v in message.si_vector:
            rvf1.si_vector.append(v)
        self.updateReqQ.put((rvf1.UID, rvf1, "SU"))
        return True

    def __cs_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.command = "CS"
        self.reqQ.put((node_uid, message, "CS"))
        metaname = "CS"
        rvf1 = p2654model2.rvf.protocols.SCAN_pb2.CS()
        rvf1.UID = self.child_uid
        rvf1.nrbits = message.nrbits
        for v in message.so_vector:
            rvf1.so_vector.append(v)
        self.updateReqQ.put((rvf1.UID, rvf1, "CS"))
        return True

    def __s_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.command = "S"
        self.reqQ.put((node_uid, message, "S"))
        metaname = "S"
        rvf1 = p2654model2.rvf.protocols.SCAN_pb2.S()
        rvf1.UID = self.child_uid
        rvf1.nrbits = message.nrbits
        for v in message.si_vector:
            rvf1.si_vector.append(v)
        for v in message.so_vector:
            rvf1.so_vector.append(v)
        self.updateReqQ.put((rvf1.UID, rvf1, "S"))
        return True

    def __endstate_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.command = "ENDSTATE"
        self.reqQ.put((node_uid, message, "ENDSTATE"))
        rvf1 = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
        rvf1.UID = self.child_uid
        rvf1.state = message.state
        self.updateReqQ.put((rvf1.UID, rvf1, "ENDSTATE"))
        return True

    def __csu_resp_cb(self, node_uid, message):
        if self.command != "CSU":
            raise ModelError("Invalid response sent.")
        # self.respQ.append((node_uid, message, "CSU", self.child_uid))
        self.updateRespQ.put((node_uid, message, "CSU", self.child_uid))
        return True

    def __su_resp_cb(self, node_uid, message):
        if self.command != "SU":
            raise ModelError("Invalid response sent.")
        # self.respQ.append((node_uid, message, "SU", self.child_uid))
        self.updateRespQ.put((node_uid, message, "SU", self.child_uid))
        return True

    def __cs_resp_cb(self, node_uid, message):
        if self.command != "CS":
            raise ModelError("Invalid response sent.")
        # self.respQ.append((node_uid, message, "CS", self.child_uid))
        self.updateRespQ.put((node_uid, message, "CS", self.child_uid))
        return True

    def __s_resp_cb(self, node_uid, message):
        if self.command != "S":
            raise ModelError("Invalid response sent.")
        # self.respQ.append((node_uid, message, "S", self.child_uid))
        self.updateRespQ.put((node_uid, message, "S", self.child_uid))
        return True

    def __endstate_resp_cb(self, node_uid, message):
        if self.command != "ENDSTATE":
            raise ModelError("Invalid response sent.")
        # self.respQ.append((node_uid, message, "ENDSTATE", self.child_uid))
        self.updateRespQ.put((node_uid, message, "ENDSTATE", self.child_uid))
        return True

    def __sendRequest(self, node_uid, message, metaname):
        self.logger.debug("TDRInject.__sendRequest(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = self.node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendRequestCallback(node_uid, wrapper)

    def __sendResponse(self, node_uid, message, metaname, uid):
        self.logger.debug("TDRInject.__sendResponse(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = self.command
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendResponseCallback(node_uid, wrapper)

    def __updateRequest(self, node_uid, message, metaname):
        self.logger.debug("TDRInject.__updateRequest(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.updateRequestCallback(node_uid, wrapper)

    def __updateResponse(self, node_uid, message, metaname, uid):
        self.logger.debug("TDRInject.__updateResponse(): sending {:s} RVF\n".format(metaname))
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
        self.writeln("Dumping TDRInject: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("child_uid = {:d}".format(self.child_uid))
        self.writeln("params = {:s}".format(self.params))
        self.writeln("children_uids = {:s}".format(str(self.children_uids)))
        self.writeln("command = {:s}".format(str(self.command)))
        self.dedent()
