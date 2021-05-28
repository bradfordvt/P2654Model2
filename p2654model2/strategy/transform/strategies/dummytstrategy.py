#!/usr/bin/env python
"""
    Transformation strategy built-in example for unit test case.
    Copyright (C) 2021  Bradford G. Van Treuren

    Transformation strategy built-in example for unit test case.

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
__date__ = "2021/02/12"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


from myhdl import intbv
import p2654model2.rvf.protocols.JTAG_pb2
import p2654model2.rvf.protocols.dummytest_pb2
import p2654model2.rvf.rvfmessage_pb2
from p2654model2.error.ModelError import ModelError
import p2654model2.callback.p2654callback
from queue import Queue


def ipint2int(val):
    v = 0
    i = 0
    for n in val:
        v = v + (n << (i * 32))
        i += 1
    return v


class dummytstrategy(object):
    __indent = 0

    def __init__(self):
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
        self.reqQ = Queue(maxsize=0)
        self.respQ = Queue(maxsize=0)

    def create(self, name, node_uid, children_uids, children_names, params):
        print("dummytstrategy params = {:s}".format(params))
        self.name = name
        self.node_uid = node_uid
        self.children_uids = children_uids
        self.children_names = children_names
        self.params = params
        return None

    def configure(self):
        return True

    def handleRequest(self, node_uid, msg):
        message = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        message.ParseFromString(msg)
        print("dummytstrategy handling request ({:s}).".format(message.metaname))
        if message.metaname == "S":
            s = p2654model2.rvf.protocols.dummytest_pb2.S()
            s.ParseFromString(message.serialized)
            return self.__shift_cb(node_uid, s)
        elif message.metaname == "SU":
            s = p2654model2.rvf.protocols.dummytest_pb2.SU()
            s.ParseFromString(message.serialized)
            return self.__shift_update_cb(node_uid, s)
        elif message.metaname == "CS":
            s = p2654model2.rvf.protocols.dummytest_pb2.CS()
            s.ParseFromString(message.serialized)
            return self.__capture_shift_cb(node_uid, s)
        elif message.metaname == "CSU":
            s = p2654model2.rvf.protocols.dummytest_pb2.CSU()
            s.ParseFromString(message.serialized)
            return self.__capture_shift_update_cb(node_uid, s)
        elif message.metaname == "RUNTEST":
            s = p2654model2.rvf.protocols.dummytest_pb2.RUNTEST()
            s.ParseFromString(message.serialized)
            return self.__runtest_cb(node_uid, s)
        return None

    def handleResponse(self, node_uid, msg):
        message = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        message.ParseFromString(msg)
        print("dummytstrategy handling response ({:s}).".format(message.metaname))
        if message.metaname == "SDR":
            s = p2654model2.rvf.protocols.JTAG_pb2.SDR()
            s.ParseFromString(message.serialized)
            return self.__sdr_resp_cb(node_uid, s)
        elif message.metaname == "RUNTEST":
            s = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
            s.ParseFromString(message.serialized)
            return self.__runtest_resp_cb(node_uid, s)
        elif message.metaname == "TRST":
            s = p2654model2.rvf.protocols.JTAG_pb2.TRST()
            s.ParseFromString(message.serialized)
            return self.__reset_resp_cb(node_uid, s)
        return None

    def updateRequest(self, node_uid, msg):
        pass

    def updateResponse(self, node_uid, msg):
        pass

    def getStatus(self, node_uid, timeout):
        print("dummytstrategy getStatus ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.STATUS
        rvf.message = "OK"
        rvf.code = 0
        return rvf

    def getError(self, node_uid, timeout):
        print("dummytstrategy getError ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFError()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.ERROR
        rvf.message = "UNKNOWN"
        rvf.code = 0
        return rvf

    def apply(self, node_uid, timeout=0):
        print("dummytstrategy apply()")
        pending = 0
        err = 0
        # for m in self.reqQ:
        while not self.reqQ.empty():
            m = self.reqQ.get(block=True, timeout=None)
            pending += 1
            ret = self.__sendRequest(m[0], m[1], m[2])
            if not ret:
                err += 1
        # for r in self.respQ:
        while not self.respQ.empty():
            r = self.respQ.get(block=True, timeout=None)
            pending += 1
            ret = self.__sendResponse(r[0], r[1], r[2], r[3])
            if not ret:
                err += 1
        if err:
            return -1
        elif pending:
            return 1
        else:
            return 0

    def getCallbackNames(self):
        return ["CSU", "CS", "SU", "S", "RUNTEST", "RESET"]

    def destroy(self, node_uid):
        return None

    def __shift_cb(self, node_uid, message):
        self.child_uid = message.UID
        si_vector = intbv(val=ipint2int(message.si_vector), _nrbits=message.nrbits)
        so_vector = intbv(val=ipint2int(message.si_vector), _nrbits=message.nrbits)
        rvf1 = p2654model2.rvf.protocols.JTAG_pb2.SDR()
        rvf1.UID = self.node_uid
        for v in message.si_vector:
            rvf1.tdi.append(v)
        for v in message.so_vector:
            rvf1.tdo.append(v)
            rvf1.mask.append(0xFFFFFFFF)
        self.command = "S"
        # self.reqQ.append((node_uid, rvf1, "SDR"))
        self.reqQ.put((node_uid, rvf1, "SDR"))
        return True

    def __shift_update_cb(self, node_uid, message):
        self.child_uid = message.UID
        si_vector = intbv(val=ipint2int(message.si_vector), _nrbits=message.nrbits)
        rvf1 = p2654model2.rvf.protocols.JTAG_pb2.SDR()
        rvf1.UID = self.node_uid
        for v in message.si_vector:
            rvf1.tdi.append(v)
            rvf1.tdo.append(0)
            rvf1.mask.append(0)
        self.command = "SU"
        # self.reqQ.append((node_uid, rvf1, "SDR"))
        self.reqQ.put((node_uid, rvf1, "SDR"))
        return True

    def __capture_shift_cb(self, node_uid, message):
        self.child_uid = message.UID
        so_vector = intbv(val=ipint2int(message.so_vector), _nrbits=message.nrbits)
        rvf1 = p2654model2.rvf.protocols.JTAG_pb2.SDR()
        rvf1.UID = self.node_uid
        for v in message.so_vector:
            rvf1.tdi.append(0)
            rvf1.tdo.append(v)
            rvf1.mask.append(0xFFFFFFFF)
        self.command = "CS"
        # self.reqQ.append((node_uid, rvf1, "SDR"))
        self.reqQ.put((node_uid, rvf1, "SDR"))
        return True

    def __capture_shift_update_cb(self, node_uid, message):
        self.child_uid = message.UID
        si_vector = intbv(val=ipint2int(message.si_vector), _nrbits=message.nrbits)
        so_vector = intbv(val=ipint2int(message.so_vector), _nrbits=message.nrbits)
        rvf1 = p2654model2.rvf.protocols.JTAG_pb2.SDR()
        rvf1.UID = self.node_uid
        for v in message.si_vector:
            rvf1.tdi.append(v)
        for v in message.so_vector:
            rvf1.tdo.append(v)
            rvf1.mask.append(0xFFFFFFFF)
        self.command = "CSU"
        # self.reqQ.append((node_uid, rvf1, "SDR"))
        self.reqQ.put((node_uid, rvf1, "SDR"))
        return True

    def __runtest_cb(self, node_uid, message):
        self.child_uid = message.UID
        rvf1 = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
        rvf1.UID = self.node_uid
        rvf1.clocks = message.clocks
        self.command = "RUNTEST"
        # self.reqQ.append((node_uid, rvf1, "RUNTEST"))
        self.reqQ.put((node_uid, rvf1, "RUNTEST"))
        return True

    def __reset_cb(self, node_uid, message):
        self.child_uid = message.UID
        rvf1 = p2654model2.rvf.protocols.JTAG_pb2.TRST()
        rvf1.UID = self.node_uid
        self.command = "TRST"
        # self.reqQ.append((node_uid, rvf1, "TRST"))
        self.reqQ.put((node_uid, rvf1, "TRST"))
        return True

    def __sdr_resp_cb(self, node_uid, message):
        rvf1 = None
        metaname = None
        if self.command == "CSU":
            metaname = "CSU"
            rvf1 = p2654model2.rvf.protocols.dummytest_pb2.CSU()
            rvf1.UID = self.child_uid
            rvf1.nrbits = message.nrbits
            for v in message.tdi:
                rvf1.si_vector.append(v)
            for v in message.tdo:
                rvf1.so_vector.append(v)
            self.__updateDataValue(node_uid, message.tdo)
        elif self.command == "CS":
            metaname = "CS"
            rvf1 = p2654model2.rvf.protocols.dummytest_pb2.CS()
            rvf1.UID = self.child_uid
            rvf1.nrbits = message.nrbits
            for v in message.tdo:
                rvf1.so_vector.append(v)
        elif self.command == "SU":
            metaname = "SU"
            rvf1 = p2654model2.rvf.protocols.dummytest_pb2.SU()
            rvf1.UID = self.child_uid
            rvf1.nrbits = message.nrbits
            for v in message.tdi:
                rvf1.si_vector.append(v)
        elif self.command == "S":
            metaname = "S"
            rvf1 = p2654model2.rvf.protocols.dummytest_pb2.S()
            rvf1.UID = self.child_uid
            rvf1.nrbits = message.nrbits
            for v in message.tdi:
                rvf1.si_vector.append(v)
            for v in message.tdo:
                rvf1.so_vector.append(v)
            self.__updateDataValue(node_uid, message.tdo)
        else:
            raise ModelError("Invalid response sent.")
        # self.respQ.append((node_uid, rvf1, metaname, self.child_uid))
        self.respQ.put((node_uid, rvf1, metaname, self.child_uid))
        return True

    def __runtest_resp_cb(self, node_uid, message):
        rvf1 = None
        metaname = None
        rvf1 = p2654model2.rvf.protocols.dummytest_pb2.RUNTEST()
        rvf1.UID = self.child_uid
        rvf1.clocks = message.run_count
        metaname = "RUNTEST"
        # self.respQ.append((node_uid, rvf1, metaname, self.child_uid))
        self.respQ.put((node_uid, rvf1, metaname, self.child_uid))
        return True

    def __reset_resp_cb(self, node_uid, message):
        rvf1 = None
        metaname = None
        rvf1 = p2654model2.rvf.protocols.dummytest_pb2.RESET()
        rvf1.UID = self.child_uid
        metaname = "RESET"
        return self.__sendResponse(node_uid, rvf1, metaname, self.child_uid)

    def __sendRequest(self, node_uid, message, metaname):
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = self.node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendRequestCallback(node_uid, wrapper)

    def __sendResponse(self, node_uid, message, metaname, uid):
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendResponseCallback(node_uid, wrapper)

    def __updateDataValue(self, node_uid, tdo):
        dvmsg = p2654model2.rvf.rvfmessage_pb2.RVFDataValue()
        dvmsg.UID = node_uid
        dvmsg.data = tdo
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
        print("" * self.__indent, ln)

    def dump(self, indent):
        self.__indent = indent
        self.writeln("Dumping dummytstrategy: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("child_uid = {:d}".format(self.child_uid))
        self.writeln("params = {:s}".format(self.params))
        self.writeln("children_uids = {:s}".format(self.children_uids))
        self.writeln("command = {:s}".format(self.command))
        self.dedent()
