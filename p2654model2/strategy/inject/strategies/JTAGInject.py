#!/usr/bin/env python
"""
    Specialized Injection Strategy for JTAG CHAINs.
    Copyright (C) 2021  Bradford G. Van Treuren

    Specialized Injection Strategy for JTAG CHAINs.  This strategy is implemented as
    a built-in plug-in module wrapped by its own InjectionStrategy instance.  To use
    this strategy, specify the name JTAGInject as the "istrategy" field of the building block.

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


from myhdl import intbv, concat

import p2654model2.rvf.protocols.JTAG_pb2
import p2654model2.rvf.rvfmessage_pb2

import logging
from autologging import traced, logged

module_logger = logging.getLogger('p2654model2.strategy.inject.strategies.JTAGInject')


@logged
@traced
class JTAGInject(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('p2654model2.strategy.inject.strategies.JTAGInject')
        self.logger.info('Creating an instance of JTAGInject')
        self.name = None
        self.node_uid = None
        self.child_uid = None
        self.children_uids = None
        self.inject_iids = None
        self.params = None
        self.command = None
        self.sendRequestCallback = None
        self.sendResponseCallback = None
        self.updateRequestCallback = None
        self.updateResponseCallback = None
        self.tdi = []
        self.tdo = []
        self.mask = []
        self.nrbits = 0
        self.cached = False
        self.data_mode = None
        self.pending = None
        self.capture = None
        self.enddr = None
        self.endir = None
        self.runtest_message = None
        self.trst_message = None
        self.state_message = None
        self.frequency_message = None

    def create(self, name, node_uid, inject_iids, children_uids, params):
        print("JTAGInject params = {:s}".format(params))
        self.name = name
        self.node_uid = node_uid
        self.inject_iids = inject_iids
        self.children_uids = children_uids
        self.params = params
        return None

    def handleRequest(self, node_uid, message):
        self.logger.debug("JTAGInject.handleRequest(): processing {:s} RVF\n".format(message.metaname))
        print("JTAGInject handling request ({:s}).".format(message.metaname))
        if message.metaname == "ENDDR":
            s = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
            s.ParseFromString(message.serialized)
            return self.__enddr_cb(node_uid, s)
        elif message.metaname == "ENDIR":
            s = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
            s.ParseFromString(message.serialized)
            return self.__endir_cb(node_uid, s)
        elif message.metaname == "SDR":
            s = p2654model2.rvf.protocols.JTAG_pb2.SDR()
            s.ParseFromString(message.serialized)
            return self.__sdr_cb(node_uid, s)
        elif message.metaname == "SIR":
            s = p2654model2.rvf.protocols.JTAG_pb2.SIR()
            s.ParseFromString(message.serialized)
            return self.__sir_cb(node_uid, s)
        elif message.metaname == "RUNTEST":
            s = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
            s.ParseFromString(message.serialized)
            return self.__runtest_cb(node_uid, s)
        elif message.metaname == "TRST":
            s = p2654model2.rvf.protocols.JTAG_pb2.TRST()
            s.ParseFromString(message.serialized)
            return self.__trst_cb(node_uid, s)
        elif message.metaname == "STATE":
            s = p2654model2.rvf.protocols.JTAG_pb2.STATE()
            s.ParseFromString(message.serialized)
            return self.__state_cb(node_uid, s)
        elif message.metaname == "FREQUENCY":
            s = p2654model2.rvf.protocols.JTAG_pb2.FREQUENCY()
            s.ParseFromString(message.serialized)
            return self.__frequency_cb(node_uid, s)
        return None

    def handleResponse(self, node_uid, message):
        self.logger.debug("JTAGInject.handleResponse(): processing {:s} RVF\n".format(message.metaname))
        print("JTAGInject handling response ({:s}).".format(message.metaname))
        if message.metaname == "ENDDR":
            s = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
            s.ParseFromString(message.serialized)
            return self.__enddr_resp_cb(node_uid, s)
        elif message.metaname == "ENDIR":
            s = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
            s.ParseFromString(message.serialized)
            return self.__endir_resp_cb(node_uid, s)
        elif message.metaname == "SDR":
            s = p2654model2.rvf.protocols.JTAG_pb2.SDR()
            s.ParseFromString(message.serialized)
            return self.__sdr_resp_cb(node_uid, s)
        elif message.metaname == "SIR":
            s = p2654model2.rvf.protocols.JTAG_pb2.SIR()
            s.ParseFromString(message.serialized)
            return self.__sir_resp_cb(node_uid, s)
        elif message.metaname == "RUNTEST":
            s = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
            s.ParseFromString(message.serialized)
            return self.__runtest_resp_cb(node_uid, s)
        elif message.metaname == "TRST":
            s = p2654model2.rvf.protocols.JTAG_pb2.TRST()
            s.ParseFromString(message.serialized)
            return self.__trst_resp_cb(node_uid, s)
        elif message.metaname == "STATE":
            s = p2654model2.rvf.protocols.JTAG_pb2.STATE()
            s.ParseFromString(message.serialized)
            return self.__state_resp_cb(node_uid, s)
        elif message.metaname == "FREQUENCY":
            s = p2654model2.rvf.protocols.JTAG_pb2.FREQUENCY()
            s.ParseFromString(message.serialized)
            return self.__frequency_resp_cb(node_uid, s)
        return None

    def getStatus(self, node_uid, timeout):
        print("JTAGInject getStatus ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.STATUS
        rvf.message = "OK"
        rvf.code = 0
        return rvf

    def getError(self, node_uid, timeout):
        print("JTAGInject getError ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFError()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.ERROR
        rvf.message = "UNKNOWN"
        rvf.code = 0
        return rvf

    def apply(self, node_uid, timeout=0):
        self.logger.debug("JTAGInject.apply(): processing {:d} node_uid\n".format(node_uid))
        return 0

    def getCallbackNames(self):
        return ["ENDDR", "ENDIR", "SDR", "SIR", "RUNTEST", "TRST", "STATE", "FREQUENCY"]

    def destroy(self, node_uid):
        return None

    def __enddr_cb(self, node_uid, message):
        wrvf = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
        wrvf.UID = node_uid
        wrvf.state = self.enddr
        self.__sendRequest(node_uid, wrvf, "ENDDR")
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
            rvf.UID = uid
            rvf.state = message.state
            self.__updateRequest(uid, rvf, "ENDDR")
        return True

    def __endir_cb(self, node_uid, message):
        wrvf = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
        wrvf.UID = node_uid
        wrvf.state = self.enddr
        self.__sendRequest(node_uid, wrvf, "ENDIR")
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
            rvf.UID = uid
            rvf.state = message.state
            self.__updateRequest(uid, rvf, "ENDIR")
        return True

    def __sdr_cb(self, node_uid, message):
        return self.__data_cb("SDR", node_uid, message)

    def __sir_cb(self, node_uid, message):
        return self.__data_cb("SIR", node_uid, message)

    def __data_cb(self, metaname, node_uid, message):
        if not self.cached:
            self.__init_segments()
            self.cached = True
        if metaname == "SIR":
            rvf = p2654model2.rvf.protocols.JTAG_pb2.SIR()
        else:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.SDR()
        rvf.UID = node_uid
        rvf.nrbits = message.nrbits
        for v in message.tdi:
            rvf.tdi.append(v)
        for v in message.tdo:
            rvf.tdo.append(v)
        for v in message.mask:
            rvf.mask.append(v)
        self.__sendRequest(node_uid, rvf, metaname)
        tdi = self.ipint2int(message.tdi)
        tdo = self.ipint2int(message.tdo)
        mask = self.ipint2int(message.mask)
        start = 0
        end = 0
        i = 0
        for uid in self.children_uids:
            nrbits = len(self.tdi[i])
            if nrbits == 0:
                continue
            end = nrbits + end
            if metaname == "SIR":
                req = p2654model2.rvf.protocols.JTAG_pb2.SIR()
            else:
                req = p2654model2.rvf.protocols.JTAG_pb2.SDR()
            req.UID = uid
            req.tdi = self.__vector_to_list(nrbits, intbv(tdi[start:end]))
            req.tdo = self.__vector_to_list(nrbits, intbv(tdo[start:end]))
            req.mask = self.__vector_to_list(nrbits, intbv(mask[start:end]))
            req.nrbits = nrbits
            self.__updateRequest(uid, req, metaname)
            start = end
            i += 1
        return True

    def __runtest_cb(self, node_uid, message):
        rvf = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
        rvf.UID = node_uid
        rvf.run_state = message.run_state
        rvf.run_count = message.run_count
        rvf.run_clk = message.run_clk
        rvf.min_time = message.min_time
        rvf.max_time = message.max_time
        rvf.end_state = message.end_state
        self.__sendRequest(node_uid, rvf, "RUNTEST")
        for uid in self.children_uids:
            crvf = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
            crvf.UID = uid
            crvf.run_state = message.run_state
            crvf.run_count = message.run_count
            crvf.run_clk = message.run_clk
            crvf.min_time = message.min_time
            crvf.max_time = message.max_time
            crvf.end_state = message.end_state
            self.__updateRequest(uid, crvf, "RUNTEST")
        return True

    def __trst_cb(self, node_uid, message):
        wrvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
        wrvf.UID = node_uid
        wrvf.state = message.state
        self.__sendRequest(node_uid, wrvf, "TRST")
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
            rvf.UID = uid
            rvf.state = message.state
            self.__updateRequest(uid, rvf, "TRST")
        return True

    def __state_cb(self, node_uid, message):
        wrvf = p2654model2.rvf.protocols.JTAG_pb2.STATE()
        wrvf.UID = node_uid
        for s in message.state:
            wrvf.state.append(s)
        wrvf.end_state = message.end_state
        self.__sendRequest(node_uid, wrvf, "STATE")
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.STATE()
            rvf.UID = uid
            for s in message.state:
                rvf.state.append(s)
            rvf.end_state = message.end_state
            self.__updateRequest(uid, rvf, "STATE")
        return True

    def __frequency_cb(self, node_uid, message):
        wrvf = p2654model2.rvf.protocols.JTAG_pb2.FREQUENCY()
        wrvf.UID = node_uid
        wrvf.cycles = message.cycles
        self.__sendRequest(node_uid, wrvf, "FREQUENCY")
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.FREQUENCY()
            rvf.UID = uid
            rvf.cycles = message.cycles
            self.__updateRequest(uid, rvf, "FREQUENCY")
        return True

    def __enddr_resp_cb(self, node_uid, message):
        wrvf = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
        wrvf.state = message.state
        self.__sendResponse(node_uid, wrvf, "ENDDR")
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
            rvf.UID = uid
            rvf.state = message.state
            self.__updateResponse(node_uid, rvf, "ENDDR", uid)
        return True

    def __endir_resp_cb(self, node_uid, message):
        wrvf = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
        wrvf.state = message.state
        self.__sendResponse(node_uid, wrvf, "ENDIR")
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
            rvf.UID = uid
            rvf.state = message.state
            self.__updateResponse(node_uid, rvf, "ENDIR", uid)
        return True

    def __sdr_resp_cb(self, node_uid, message):
        return self.__data_resp("SDR", node_uid, message)

    def __sir_resp_cb(self, node_uid, message):
        return self.__data_resp("SIR", node_uid, message)

    def __data_resp(self, metaname, node_uid, message):
        if metaname == "SIR":
            rvf = p2654model2.rvf.protocols.JTAG_pb2.SIR()
        else:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.SDR()
        rvf.UID = node_uid
        rvf.nrbits = message.nrbits
        for v in message.tdi:
            rvf.tdi.append(v)
        for v in message.tdo:
            rvf.tdo.append(v)
        for v in message.mask:
            rvf.mask.append(v)
        self.__sendResponse(node_uid, rvf, metaname)
        tdi = self.ipint2int(message.tdi)
        tdo = self.ipint2int(message.tdo)
        mask = self.ipint2int(message.mask)
        start = 0
        end = 0
        i = 0
        for uid in self.children_uids:
            nrbits = len(self.tdi[i])
            end = nrbits + end
            if metaname == "SIR":
                resp = p2654model2.rvf.protocols.JTAG_pb2.SIR()
            else:
                resp = p2654model2.rvf.protocols.JTAG_pb2.SDR()
            resp.UID = uid
            resp.tdi = self.__vector_to_list(nrbits, intbv(tdi[start:end]))
            resp.tdo = self.__vector_to_list(nrbits, intbv(tdo[start:end]))
            resp.mask = self.__vector_to_list(nrbits, intbv(mask[start:end]))
            resp.nrbits = nrbits
            self.__updateResponse(node_uid, resp, metaname, uid)
            start = end
            i += 1

    def __runtest_resp_cb(self, node_uid, message):
        wrvf = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
        wrvf.UID = node_uid
        wrvf.run_state = message.run_state
        wrvf.run_count = message.run_count
        wrvf.run_clk = message.run_clk
        wrvf.min_time = message.min_time
        wrvf.max_time = message.max_time
        wrvf.end_state = message.end_state
        self.__sendResponse(node_uid, wrvf, "RUNTEST")
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
            rvf.UID = uid
            rvf.run_state = message.run_state
            rvf.run_count = message.run_count
            rvf.run_clk = message.run_clk
            rvf.min_time = message.min_time
            rvf.max_time = message.max_time
            rvf.end_state = message.end_state
            self.__updateResponse(node_uid, rvf, "RUNTEST", uid)
        return True

    def __trst_resp_cb(self, node_uid, message):
        wrvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
        wrvf.UID = node_uid
        wrvf.state = message.state
        self.__sendResponse(node_uid, wrvf, "TRST")
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
            rvf.UID = uid
            rvf.state = message.state
            self.__updateResponse(node_uid, rvf, "TRST", uid)
        return True

    def __state_resp_cb(self, node_uid, message):
        wrvf = p2654model2.rvf.protocols.JTAG_pb2.STATE()
        wrvf.UID = node_uid
        for s in self.state_message.state:
            wrvf.state.append(s)
        wrvf.end_state = self.state_message.end_state
        self.__sendResponse(node_uid, wrvf, "STATE")
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.STATE()
            rvf.UID = uid
            for s in self.state_message.state:
                rvf.state.append(s)
            rvf.end_state = self.state_message.end_state
            self.__updateResponse(node_uid, rvf, "STATE", uid)
        return True

    def __frequency_resp_cb(self, node_uid, message):
        wrvf = p2654model2.rvf.protocols.JTAG_pb2.FREQUENCY()
        wrvf.UID = node_uid
        wrvf.cycles = message.cycles
        self.__sendResponse(node_uid, wrvf, "FREQUENCY")
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.FREQUENCY()
            rvf.UID = uid
            rvf.cycles = message.cycles
            self.__updateResponse(node_uid, rvf, "FREQUENCY", uid)
        return True

    def __sendRequest(self, node_uid, message, metaname):
        self.logger.debug("JTAGInject.__sendRequest(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = self.node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendRequestCallback(node_uid, wrapper.SerializeToString())

    def __sendResponse(self, node_uid, message, metaname):
        self.logger.debug("JTAGInject.__sendResponse(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = node_uid
        wrapper.metaname = self.command
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendResponseCallback(node_uid, wrapper.SerializeToString())

    def __updateRequest(self, node_uid, message, metaname):
        self.logger.debug("JTAGInject.__updateRequest(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.updateRequestCallback(node_uid, wrapper.SerializeToString())

    def __updateResponse(self, node_uid, message, metaname, uid):
        self.logger.debug("JTAGInject.__updateResponse(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.updateResponseCallback(node_uid, wrapper.SerializeToString())

    def set_sendRequestCallback(self, callback):
        self.sendRequestCallback = callback

    def set_sendResponseCallback(self, callback):
        self.sendResponseCallback = callback

    def set_updateRequestCallback(self, callback):
        self.updateRequestCallback = callback

    def set_updateResponseCallback(self, callback):
        self.updateResponseCallback = callback

    def __subsegment_count(self):
        seg_count = len(self.children_uids)
        return seg_count

    def __init_segments(self):
        scsize = self.__subsegment_count()
        self.tdi = []
        self.tdo = []
        self.mask = []
        for i in range(scsize):
            self.tdi.append(intbv(0))
            self.tdo.append(intbv(0))
            self.mask.append(intbv(0))

    @staticmethod
    def __vector_to_list(size, value):
        bvlist = []
        bv = intbv(value)
        words = (size + 31) / 32
        while words:
            bvlist.append(bv & 0xFFFFFFFF)
            bv = bv >> 32
        return bvlist

    @staticmethod
    def ipint2int(val):
        v = 0
        i = 0
        for n in val:
            v = v + (n << (i * 32))
            i += 1
        return v

    def indent(self):
        self.__indent += 4

    def dedent(self):
        self.__indent -= 4

    def writeln(self, ln):
        print("" * self.__indent, ln)

    def dump(self, indent):
        self.__indent = indent
        self.writeln("Dumping JTAGInject: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("child_uid = {:d}".format(self.child_uid))
        self.writeln("params = {:s}".format(self.params))
        self.writeln("children_uids = {:s}".format(self.children_uids))
        self.writeln("command = {:s}".format(self.command))
        self.dedent()
