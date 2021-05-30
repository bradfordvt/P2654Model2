#!/usr/bin/env python
"""
    Specialized Transformation Strategy for JTAG CONTROLLERs in the P2654Simulations tester.
    Copyright (C) 2021  Bradford G. Van Treuren

    Specialized Transformation Strategy for JTAG CONTROLLERs in the P2654Simulations tester.
    This strategy is implemented as a built-in plug-in module wrapped by its own TransformationStrategy
    instance.  To use this strategy, specify the name JTAGControllerAssembly as the "tstrategy"
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
from myhdl import intbv, concat
import p2654model2.rvf.protocols.JTAG_pb2
import p2654model2.rvf.rvfmessage_pb2
from p2654model2.builder.drivers import Drivers
from p2654model2.error.ModelError import ModelError
from drivers.ate.atesim import RUN_TEST_IDLE, SHIFT_IR, SHIFT_DR, PAUSE_DR, PAUSE_IR, TEST_LOGIC_RESET

# create logger
module_logger = logging.getLogger('p2654model2.strategy.transform.strategies.JTAGControllerAssembly')


@logged
@traced
class JTAGControllerAssembly(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('P2654Model.transform.strategies.JTAGControllerAssembly.JTAGControllerAssembly')
        self.logger.info('Creating an instance of JTAGControllerAssembly')
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
        self.tdi = None
        self.tdo = None
        self.mask = None
        self.nrbits = 0
        self.cached = False
        self.data_mode = None
        self.pending = None
        self.capture = None
        self.enddr = RUN_TEST_IDLE
        self.endir = RUN_TEST_IDLE
        self.startdr = SHIFT_DR
        self.startir = SHIFT_IR
        self.runtest_message = None
        self.trst_message = None
        self.state_message = None
        self.frequency_message = None
        self.jtag_controller = Drivers.get_jtag()

    def create(self, name, node_uid, children_uids, children_names, params):
        # print("JTAGControllerAssembly params = {:s}".format(str(params)))
        self.name = name
        self.node_uid = node_uid
        self.children_uids = children_uids
        self.children_names = children_names
        self.params = params
        return None

    def configure(self):
        return True

    def handleRequest(self, node_uid, message):
        self.logger.debug("JTAGControllerAssembly.handleRequest(): processing {:s} RVF\n".format(message.metaname))
        print("JTAGControllerAssembly handling request ({:s}).".format(message.metaname))
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
        self.logger.debug("JTAGControllerAssembly.handleResponse(): processing {:s} RVF\n".format(message.metaname))
        print("JTAGControllerAssembly handling response ({:s}).".format(message.metaname))
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
        print("JTAGControllerAssembly getStatus ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.STATUS
        rvf.message = "OK"
        rvf.code = 0
        return rvf

    def getError(self, node_uid, timeout):
        print("JTAGControllerAssembly getError ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFError()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.ERROR
        rvf.message = "UNKNOWN"
        rvf.code = 0
        return rvf

    def apply(self, node_uid, timeout=0):
        self.logger.debug("JTAGControllerAssembly.apply(): processing {:d} node_uid\n".format(node_uid))
        print("JTAGControllerAssembly apply()")
        pending = 0
        err = 0
        if self.pending:
            if self.data_mode is None:
                raise ModelError("Pending conflict with data_mode!")
            if self.runtest_message is not None:
                self.jtag_controller.runtest(self.runtest_message.run_count)
                wrvf = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
                wrvf.UID = self.child_uid
                wrvf.run_state = self.runtest_message.run_state
                wrvf.run_count = self.runtest_message.run_count
                wrvf.run_clk = self.runtest_message.run_clk
                wrvf.min_time = self.runtest_message.min_time
                wrvf.max_time = self.runtest_message.max_time
                wrvf.end_state = self.runtest_message.end_state
                pending += 1
                ret = self.__sendResponse(node_uid, wrvf, "RUNTEST", self.child_uid)
                if not ret:
                    err +=1
                self.runtest_message = None
            if self.trst_message is not None:
                if self.trst_message.state:
                    self.jtag_controller.softreset()
                wrvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
                wrvf.UID = self.child_uid
                wrvf.state = self.trst_message.state
                pending += 1
                ret = self.__sendResponse(node_uid, wrvf, "TRST", self.child_uid)
                if not ret:
                    err += 1
                self.trst_message = None
            if self.state_message is not None:
                raise NotImplementedError("Support for state is not yet implemented.")
                # wrvf = p2654model2.rvf.protocols.JTAG_pb2.STATE()
                # wrvf.UID = node_uid
                # for s in self.state_message.state:
                #     wrvf.state.append(s)
                # wrvf.end_state = self.state_message.end_state
                # self.__sendRequest(node_uid, wrvf, "STATE")
                # self.state_message = None
            if self.frequency_message is not None:
                raise NotImplementedError("Support for frequency is not yet implemented.")
                # wrvf = p2654model2.rvf.protocols.JTAG_pb2.FREQUENCY()
                # wrvf.UID = node_uid
                # wrvf.cycles = self.frequency_message.cycles
                # self.__sendRequest(node_uid, wrvf, "FREQUENCY")
                # self.frequency_message = None
            if self.capture and self.data_mode:
                hextdi = JTAGControllerAssembly.intbv2hexstring(self.tdi)
                tdo = self.jtag_controller.scan_dr(len(self.tdi), hextdi, end=self.enddr)  # self.tdi must be an intbv type
                wrvf = p2654model2.rvf.protocols.JTAG_pb2.SDR()
                wrvf.UID = node_uid
                self.nrbits = len(self.tdi)
                wrvf.nrbits = self.nrbits
                ltdi = self.__vector_to_list(self.nrbits, self.tdi)
                for v in ltdi:
                    wrvf.tdi.append(v)
                ltdo = self.__vector_to_list(self.nrbits, intbv(int("0x" + tdo, 16), _nrbits=len(self.tdi)))
                for v in ltdo:
                    wrvf.tdo.append(v)
                lmask = self.__vector_to_list(self.nrbits, self.mask)
                for v in lmask:
                    wrvf.mask.append(v)
                pending += 1
                ret = self.__sendResponse(node_uid, wrvf, "SDR", self.child_uid)
                if not ret:
                    err += 1
                self.pending = False
                self.capture = False
                self.data_mode = None
            elif self.capture and not self.data_mode:
                hextdi = JTAGControllerAssembly.intbv2hexstring(self.tdi)
                tdo = self.jtag_controller.scan_ir(len(self.tdi), hextdi, end=self.endir)  # self.tdi must be an intbv type
                wrvf = p2654model2.rvf.protocols.JTAG_pb2.SIR()
                wrvf.UID = node_uid
                self.nrbits = len(self.tdi)
                wrvf.nrbits = self.nrbits
                ltdi = self.__vector_to_list(self.nrbits, self.tdi)
                for v in ltdi:
                    wrvf.tdi.append(v)
                ltdo = self.__vector_to_list(self.nrbits, intbv(int("0x" + tdo, 16), _nrbits=len(self.tdi)))
                for v in ltdo:
                    wrvf.tdo.append(v)
                lmask = self.__vector_to_list(self.nrbits, self.mask)
                for v in lmask:
                    wrvf.mask.append(v)
                pending += 1
                ret = self.__sendResponse(node_uid, wrvf, "SIR", self.child_uid)
                if not ret:
                    err += 1
                self.pending = False
                self.capture = False
                self.data_mode = None
        if err:
            return -1
        elif pending:
            return 1
        else:
            return 0

    def getCallbackNames(self):
        return ["ENDDR", "ENDIR", "SDR", "SIR", "RUNTEST", "TRST", "STATE", "FREQUENCY"]

    def destroy(self, node_uid):
        return None

    def get_size(self):
        return self.nrbits

    def __enddr_cb(self, node_uid, message):
        self.child_uid = message.UID
        if message.state == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.TLR_STABLE:
            self.enddr = TEST_LOGIC_RESET
        elif message.state == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.IDLE_STABLE:
            self.enddr = RUN_TEST_IDLE
        elif message.state == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.DRPAUSE_STABLE:
            self.enddr = PAUSE_DR
        elif message.state == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.IRPAUSE_STABLE:
            self.enddr = PAUSE_IR
        else:
            raise AssertionError("Invalid enddr state detected.")
        self.pending = True
        return True

    def __endir_cb(self, node_uid, message):
        self.child_uid = message.UID
        if message.state == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.TLR_STABLE:
            self.endir = TEST_LOGIC_RESET
        elif message.state == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.IDLE_STABLE:
            self.endir = RUN_TEST_IDLE
        elif message.state == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.DRPAUSE_STABLE:
            self.endir = PAUSE_DR
        elif message.state == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.IRPAUSE_STABLE:
            self.endir = PAUSE_IR
        else:
            raise AssertionError("Invalid endir state detected.")
        self.pending = True
        return True

    def __sdr_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.tdi = intbv(self.ipint2int(message.tdi), min=None, max=None, _nrbits=message.nrbits)
        self.tdo = intbv(self.ipint2int(message.tdo), min=None, max=None, _nrbits=message.nrbits)
        self.mask = intbv(self.ipint2int(message.mask), min=None, max=None, _nrbits=message.nrbits)
        self.pending = True
        self.capture = True
        self.data_mode = True
        self.__updateDataValue(node_uid, message)
        return True

    def __sir_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.tdi = intbv(self.ipint2int(message.tdi), min=None, max=None, _nrbits=message.nrbits)
        self.tdo = intbv(self.ipint2int(message.tdo), min=None, max=None, _nrbits=message.nrbits)
        self.mask = intbv(self.ipint2int(message.mask), min=None, max=None, _nrbits=message.nrbits)
        self.pending = True
        self.capture = True
        self.data_mode = False
        self.__updateDataValue(node_uid, message)
        return True

    def __runtest_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.runtest_message = message
        self.pending = True
        return True

    def __trst_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.trst_message = message
        self.pending = True
        return True

    def __state_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.state_message = message
        self.pending = True
        return True

    def __frequency_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.frequency_message = message
        self.pending = True
        return True

    def __enddr_resp_cb(self, node_uid, message):
        return True

    def __endir_resp_cb(self, node_uid, message):
        return True

    def __sdr_resp_cb(self, node_uid, message):
        self.__updateDataValue(node_uid, message)
        return True

    def __sir_resp_cb(self, node_uid, message):
        self.__updateDataValue(node_uid, message)
        return True

    def __runtest_resp_cb(self, node_uid, message):
        return True

    def __trst_resp_cb(self, node_uid, message):
        return True

    def __state_resp_cb(self, node_uid, message):
        return True

    def __frequency_resp_cb(self, node_uid, message):
        return True

    def __sendRequest(self, node_uid, message, metaname):
        self.logger.debug("JTAGControllerAssembly.__sendRequest(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = self.node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendRequestCallback(node_uid, wrapper)

    def __sendResponse(self, node_uid, message, metaname, uid):
        self.logger.debug("JTAGControllerAssembly.__sendResponse(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendResponseCallback(node_uid, wrapper)

    def __updateDataValue(self, node_uid, message):
        self.logger.debug("JTAGControllerAssembly.__updateDataValue({:s}):\n".format(self.name))
        dvmsg = p2654model2.rvf.rvfmessage_pb2.RVFDataValue()
        dvmsg.UID = node_uid
        dvmsg.nrbits = message.nrbits
        for v in message.tdo:
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

    @staticmethod
    def __vector_to_list(size, value):
        bvlist = []
        bv = intbv(value)
        words = (size + 31) // 32
        while words:
            bvlist.append(bv & 0xFFFFFFFF)
            bv = bv >> 32
            words -= 1
        return bvlist

    @staticmethod
    def ipint2int(val):
        v = 0
        i = 0
        for n in val:
            v = v + (n << (i * 32))
            i += 1
        return v

    @staticmethod
    def intbv2hexstring(i):
        _nrbits = len(i)
        _chars = (_nrbits + 3) // 4
        return "{0:0{1}X}".format(int(i), _chars)

    def indent(self):
        self.__indent += 4

    def dedent(self):
        self.__indent -= 4

    def writeln(self, ln):
        print(" " * self.__indent, ln)

    def dump(self, indent):
        self.__indent = indent
        self.writeln("Dumping JTAGControllerAssembly: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("child_uid = {:s}".format(str(self.child_uid)))
        self.writeln("params = {:s}".format(str(self.params)))
        self.writeln("children_uids = {:s}".format(str(self.children_uids)))
        self.dedent()
