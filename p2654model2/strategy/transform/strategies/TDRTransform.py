#!/usr/bin/env python
"""
    Specialized Transformation Strategy for TDR REGISTERs.
    Copyright (C) 2021  Bradford G. Van Treuren

    Specialized Transformation Strategy for TDR REGISTERs.
    This strategy is implemented as a built-in plug-in module wrapped by its own TransformationStrategy
    instance.  To use this strategy, specify the name TDRTransform as the "tstrategy"
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
__date__ = "2021/03/03"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


import p2654model2.rvf.protocols.SCAN_pb2
import p2654model2.rvf.rvfmessage_pb2


import logging
from autologging import traced, logged

module_logger = logging.getLogger('p2654model2.strategy.transforms.strategies.TDRTransform')


@logged
@traced
class TDRTransform(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('p2654model2.strategy.transforms.strategies.TDRTransform')
        self.logger.info('Creating an instance of TDRTransform')
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
        self.si = []
        self.so = []
        self.nrbits = None
        self.status_message = "OK"
        self.status_code = 0
        self.error_message = "UNKNOWN"
        self.error_code = 0
        self.observers = []

    def create(self, name, node_uid, children_uids, children_names, params):
        # print("TDRTransform params = {:s}".format(params))
        self.name = name
        self.node_uid = node_uid
        self.children_uids = children_uids
        self.children_names = children_names
        self.params = params
        return None

    def configure(self):
        return True

    def handleRequest(self, node_uid, msg):
        self.logger.debug("TDRTransform.handleRequest({:s}): processing {:s} RVF\n".format(self.name, msg.metaname))
        # print("TDRTransform handling request ({:s}).".format(msg.metaname))
        raise AssertionError("handleRequest called for leaf TDRTransform.")

    def handleResponse(self, node_uid, msg):
        self.logger.debug("TDRTransform.handleResponse({:s}): processing {:s} RVF\n".format(self.name, msg.metaname))
        # print("TDRTransform handling response ({:s}).".format(msg.metaname))
        raise AssertionError("handleResponse called for leaf TDRTransform.")

    def updateRequest(self, node_uid, message):
        self.logger.debug("TDRTransform.updateRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        self.status_message = "OK"
        self.status_code = 0
        self.error_message = "UNKNOWN"
        self.error_code = 0
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
        return 0

    def updateResponse(self, node_uid, message):
        self.logger.debug("TDRTransform.updateResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        if message.metaname == "ERROR":
            s = p2654model2.rvf.rvfmessage_pb2.RVFError()
            s.ParseFromString(message.serialized)
            self.error_message = s.message
            self.error_code = s.code
            return True
        elif message == "STATUS":
            s = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
            s.ParseFromString(message.serialized)
            self.status_message = s.message
            self.status_code = s.code
            return True
        elif message.metaname == "CSU":
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
        elif message.metaname == "S":
            s = p2654model2.rvf.protocols.SCAN_pb2.S()
            s.ParseFromString(message.serialized)
            return self.__s_resp_cb(node_uid, s)
        elif message.metaname == "ENDSTATE":
            s = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
            s.ParseFromString(message.serialized)
            return self.__endstate_resp_cb(node_uid, s)
        return 0

    def getStatus(self, node_uid, timeout):
        print("TDRTransform getStatus ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
        rvf.UID = self.node_uid
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.STATUS
        rvf.message = self.status_message
        rvf.code = self.status_code
        return rvf

    def getError(self, node_uid, timeout):
        print("TDRTransform getError ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFError()
        rvf.UID = self.node_uid
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.ERROR
        rvf.message = self.error_message
        rvf.code = self.status_code
        return rvf

    def apply(self, node_uid, timeout=0):
        self.logger.debug("TDRTransform.apply({:s}): processing {:d} node_uid\n".format(self.name, node_uid))
        print("TDRTransform apply()")
        return 0

    def getCallbackNames(self):
        return ["CSU", "CS", "SU", "S", "RUNLOOP", "RESET", "ENDSTATE"]

    def destroy(self, node_uid):
        return None

    def __csu_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.si = []
        self.nrbits = message.nrbits
        for v in message.si_vector:
            self.si.append(v)
        return True

    def __su_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.si = []
        self.nrbits = message.nrbits
        for v in message.si_vector:
            self.si.append(v)
        return True

    def __cs_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.nrbits = message.nrbits
        return True

    def __s_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.si = []
        self.nrbits = message.nrbits
        for v in message.si_vector:
            self.si.append(v)
        return True

    def __endstate_cb(self, node_uid, message):
        self.child_uid = message.UID
        return True

    def __csu_resp_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.so = []
        self.nrbits = message.nrbits
        for v in message.so_vector:
            self.so.append(v)
        self.__updateDataValue(node_uid)
        return True

    def __su_resp_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.so = []
        self.nrbits = message.nrbits
        for v in message.si_vector:
            self.so.append(v)
        self.__updateDataValue(node_uid)
        return True

    def __cs_resp_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.so = []
        self.nrbits = message.nrbits
        for v in message.so_vector:
            self.so.append(v)
        self.__updateDataValue(node_uid)
        return True

    def __s_resp_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.si = []
        self.nrbits = message.nrbits
        for v in message.si_vector:
            self.si.append(v)
        self.so = []
        for v in message.so_vector:
            self.so.append(v)
        self.__updateDataValue(node_uid)
        return True

    def __endstate_resp_cb(self, node_uid, message):
        self.child_uid = message.UID
        return True

    def __sendRequest(self, node_uid, message, metaname):
        self.logger.debug("TDRTransform.__sendRequest({:s}): sending {:s} RVF\n".format(self.name, metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = self.node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendRequestCallback(node_uid, wrapper)

    def __sendResponse(self, node_uid, message, metaname, uid):
        self.logger.debug("TDRTransform.__sendResponse({:s}): sending {:s} RVF\n".format(self.name, metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendResponseCallback(node_uid, wrapper)

    def __updateDataValue(self, node_uid):
        self.logger.debug("TDRTransform.__updateDataValue({:s}):\n".format(self.name))
        dvmsg = p2654model2.rvf.rvfmessage_pb2.RVFDataValue()
        dvmsg.UID = node_uid
        dvmsg.nrbits = self.nrbits
        for v in self.so:
            dvmsg.data.append(v)
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
