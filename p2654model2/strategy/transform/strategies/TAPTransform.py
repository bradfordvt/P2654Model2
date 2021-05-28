#!/usr/bin/env python
"""
    Specialized Transformation Strategy for TAP Interface State Machine LINKERs.
    Copyright (C) 2021  Bradford G. Van Treuren

    Specialized Transformation Strategy for TAP Interface State Machine LINKERs.
    This strategy is implemented as a built-in plug-in module wrapped by its own TransformationStrategy
    instance.  To use this strategy, specify the name TAPTransform as the "tstrategy"
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


from myhdl import intbv, concat
import p2654model2.rvf.protocols.JTAG_pb2
import p2654model2.rvf.protocols.SCAN_pb2
import p2654model2.rvf.rvfmessage_pb2
from queue import Queue


import logging
from autologging import traced, logged


module_logger = logging.getLogger('p2654model2.strategy.transforms.strategies.TAPTransform')


@logged
@traced
class TAPTransform(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('p2654model2.strategy.transforms.strategies.TAPTransform')
        self.logger.info('Creating an instance of TAPTransform')
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
        # self.reqQ = []
        # self.respQ = []
        self.reqQ = Queue(maxsize=0)
        self.respQ = Queue(maxsize=0)
        self.stable_state = None
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
        self.status_message = "OK"
        self.status_code = 0
        self.error_message = "UNKNOWN"
        self.error_code = 0

    def create(self, name, node_uid, children_uids, children_names, params):
        # print("TAPTransform params = {:s}".format(params))
        self.name = name
        self.node_uid = node_uid
        self.children_uids = children_uids
        self.children_names = children_names
        self.params = params
        return None

    def configure(self):
        return True

    def handleRequest(self, node_uid, message):
        self.logger.debug("TAPTransform.handleRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        print("TAPTransform handling request ({:s}).".format(message.metaname))
        self.status_message = "OK"
        self.status_code = 0
        self.error_message = "UNKNOWN"
        self.error_code = 0
        if message.metaname == "SU":
            s = p2654model2.rvf.protocols.SCAN_pb2.SU()
            s.ParseFromString(message.serialized)
            return self.__su_cb(node_uid, s)
        elif message.metaname == "CS":
            s = p2654model2.rvf.protocols.SCAN_pb2.CS()
            s.ParseFromString(message.serialized)
            return self.__cs_cb(node_uid, s)
        elif message.metaname == "CSU":
            s = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            s.ParseFromString(message.serialized)
            return self.__csu_cb(node_uid, s)
        elif message.metaname == "S":
            s = p2654model2.rvf.protocols.SCAN_pb2.S()
            s.ParseFromString(message.serialized)
            return self.__s_cb(node_uid, s)
        elif message.metaname == "RUNLOOP":
            s = p2654model2.rvf.protocols.SCAN_pb2.RUNLOOP()
            s.ParseFromString(message.serialized)
            return self.__runloop_cb(node_uid, s)
        elif message.metaname == "RESET":
            s = p2654model2.rvf.protocols.SCAN_pb2.RESET()
            s.ParseFromString(message.serialized)
            return self.__reset_cb(node_uid, s)
        elif message.metaname == "ENDSTATE":
            s = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
            s.ParseFromString(message.serialized)
            return self.__endstate_cb(node_uid, s)
        return None

    def handleResponse(self, node_uid, message):
        self.logger.debug("TAPTransform.handleResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        print("TAPTransform handling response ({:s}).".format(message.metaname))
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
        elif message.metaname == "ENDDR":
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
        return None

    def updateRequest(self, node_uid, message):
        self.logger.debug("TAPTransform.updateRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        self.status_message = "OK"
        self.status_code = 0
        self.error_message = "UNKNOWN"
        self.error_code = 0
        if message.metaname == "ENDDR":
            s = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
            s.ParseFromString(message.serialized)
            return self.__update_enddr_cb(node_uid, s)
        elif message.metaname == "ENDIR":
            s = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
            s.ParseFromString(message.serialized)
            return self.__update_endir_cb(node_uid, s)
        elif message.metaname == "SDR":
            s = p2654model2.rvf.protocols.JTAG_pb2.SDR()
            s.ParseFromString(message.serialized)
            return self.__update_sdr_cb(node_uid, s)
        elif message.metaname == "SIR":
            s = p2654model2.rvf.protocols.JTAG_pb2.SIR()
            s.ParseFromString(message.serialized)
            return self.__update_sir_cb(node_uid, s)
        elif message.metaname == "RUNTEST":
            s = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
            s.ParseFromString(message.serialized)
            return self.__update_runtest_cb(node_uid, s)
        elif message.metaname == "TRST":
            s = p2654model2.rvf.protocols.JTAG_pb2.TRST()
            s.ParseFromString(message.serialized)
            return self.__update_trst_cb(node_uid, s)
        elif message.metaname == "STATE":
            s = p2654model2.rvf.protocols.JTAG_pb2.STATE()
            s.ParseFromString(message.serialized)
            return self.__update_state_cb(node_uid, s)
        elif message.metaname == "FREQUENCY":
            s = p2654model2.rvf.protocols.JTAG_pb2.FREQUENCY()
            s.ParseFromString(message.serialized)
            return self.__update_frequency_cb(node_uid, s)
        return 0

    def updateResponse(self, node_uid, message):
        self.logger.debug("TAPTransform.updateResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
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
        elif message.metaname == "ENDDR":
            s = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
            s.ParseFromString(message.serialized)
            return self.__update_enddr_resp_cb(node_uid, s)
        elif message.metaname == "ENDIR":
            s = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
            s.ParseFromString(message.serialized)
            return self.__update_endir_resp_cb(node_uid, s)
        elif message.metaname == "SDR":
            s = p2654model2.rvf.protocols.JTAG_pb2.SDR()
            s.ParseFromString(message.serialized)
            return self.__update_sdr_resp_cb(node_uid, s)
        elif message.metaname == "SIR":
            s = p2654model2.rvf.protocols.JTAG_pb2.SIR()
            s.ParseFromString(message.serialized)
            return self.__update_sir_resp_cb(node_uid, s)
        elif message.metaname == "RUNTEST":
            s = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
            s.ParseFromString(message.serialized)
            return self.__update_runtest_resp_cb(node_uid, s)
        elif message.metaname == "TRST":
            s = p2654model2.rvf.protocols.JTAG_pb2.TRST()
            s.ParseFromString(message.serialized)
            return self.__update_trst_resp_cb(node_uid, s)
        elif message.metaname == "STATE":
            s = p2654model2.rvf.protocols.JTAG_pb2.STATE()
            s.ParseFromString(message.serialized)
            return self.__update_state_resp_cb(node_uid, s)
        elif message.metaname == "FREQUENCY":
            s = p2654model2.rvf.protocols.JTAG_pb2.FREQUENCY()
            s.ParseFromString(message.serialized)
            return self.__update_frequency_resp_cb(node_uid, s)
        return 0

    def getStatus(self, node_uid, timeout):
        print("TAPTransform getStatus ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.STATUS
        rvf.message = "OK"
        rvf.code = 0
        return rvf

    def getError(self, node_uid, timeout):
        print("TAPTransform getError ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFError()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.ERROR
        rvf.message = "UNKNOWN"
        rvf.code = 0
        return rvf

    def apply(self, node_uid, timeout=0):
        self.logger.debug("TAPTransform.apply({:s}): processing {:d} node_uid\n".format(self.name, node_uid))
        print("TAPTransform apply()")
        pending = 0
        err = 0
        # for m in self.reqQ:
        while not self.reqQ.empty():
            m = self.reqQ.get(block=True, timeout=None)
            pending += 1
            ret = self.__sendRequest(m[0], m[1], m[2])
            if not ret:
                self.status_message = "ERROR"
                self.error_message = "TAPTransform.apply({:s}): {:d} node_uid failed to send request".format(self.name,
                                                                                                             node_uid)
                err += 1
        # for r in self.respQ:
        while not self.respQ.empty():
            r = self.respQ.get(block=True, timeout=None)
            pending += 1
            ret = self.__sendResponse(r[0], r[1], r[2], r[3])
            if not ret:
                self.status_message = "ERROR"
                self.error_message = "TAPTransform.apply({:s}): {:d} node_uid failed to send request".format(self.name,
                                                                                                             node_uid)
                err += 1
        if err:
            self.status_code = -1
            self.error_code = err
            return -1
        elif pending:
            return 1
        else:
            return 0

    def getCallbackNames(self):
        return ["CSU", "SU", "CS", "S", "RUNLOOP", "RESET", "ENDSTATE"]

    def destroy(self, node_uid):
        return None

    def __su_cb(self, node_uid, message):
        self.command = "SU"
        if message.UID == self.children_uids[0]:  # The Instruction Register message
            rvf = p2654model2.rvf.protocols.JTAG_pb2.SIR()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.si_vector:
                rvf.tdi.append(v)
            self.pending = True
            self.data_mode = False
            # self.reqQ.append((node_uid, rvf, "SIR"))
            self.reqQ.put((node_uid, rvf, "SIR"))
        else:  # DRMUX paths
            rvf = p2654model2.rvf.protocols.JTAG_pb2.SDR()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.si_vector:
                rvf.tdi.append(v)
            self.pending = True
            self.data_mode = True
            # self.reqQ.append((node_uid, rvf, "SDR"))
            self.reqQ.put((node_uid, rvf, "SDR"))
        return True

    def __cs_cb(self, node_uid, message):
        self.command = "CS"
        if message.UID == self.children_uids[0]:  # The Instruction Register message
            rvf = p2654model2.rvf.protocols.JTAG_pb2.SIR()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.so_vector:
                rvf.tdo.append(v)
                rvf.mask.append(0xFFFFFFFF)
            self.pending = True
            self.data_mode = False
            # self.reqQ.append((node_uid, rvf, "SIR"))
            self.reqQ.put((node_uid, rvf, "SIR"))
        else:  # DRMUX paths
            rvf = p2654model2.rvf.protocols.JTAG_pb2.SDR()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.so_vector:
                rvf.tdo.append(v)
                rvf.mask.append(0xFFFFFFFF)
            self.pending = True
            self.data_mode = True
            # self.reqQ.append((node_uid, rvf, "SDR"))
            self.reqQ.put((node_uid, rvf, "SDR"))
        return True

    def __csu_cb(self, node_uid, message):
        self.command = "CSU"
        if message.UID == self.children_uids[0]:  # The Instruction Register message
            rvf = p2654model2.rvf.protocols.JTAG_pb2.SIR()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.si_vector:
                rvf.tdi.append(v)
            for v in message.so_vector:
                rvf.tdo.append(v)
                rvf.mask.append(0xFFFFFFFF)
            self.pending = True
            self.data_mode = False
            # self.reqQ.append((node_uid, rvf, "SIR"))
            self.reqQ.put((node_uid, rvf, "SIR"))
        else:  # DRMUX paths
            rvf = p2654model2.rvf.protocols.JTAG_pb2.SDR()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.si_vector:
                rvf.tdi.append(v)
            for v in message.so_vector:
                rvf.tdo.append(v)
                rvf.mask.append(0xFFFFFFFF)
            self.pending = True
            self.data_mode = True
            # self.reqQ.append((node_uid, rvf, "SDR"))
            self.reqQ.put((node_uid, rvf, "SDR"))
        return True

    def __s_cb(self, node_uid, message):
        self.command = "S"
        if message.UID == self.children_uids[0]:  # The Instruction Register message
            rvf = p2654model2.rvf.protocols.JTAG_pb2.SIR()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.si_vector:
                rvf.tdi.append(v)
            for v in message.so_vector:
                rvf.tdo.append(v)
                rvf.mask.append(0xFFFFFFFF)
            # self.reqQ.append((node_uid, rvf, "SIR"))
            self.reqQ.put((node_uid, rvf, "SIR"))
            self.pending = True
            self.data_mode = False
        else:  # DRMUX paths
            rvf = p2654model2.rvf.protocols.JTAG_pb2.SDR()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.si_vector:
                rvf.tdi.append(v)
            for v in message.so_vector:
                rvf.tdo.append(v)
                rvf.mask.append(0xFFFFFFFF)
            # self.reqQ.append((node_uid, rvf, "SDR"))
            self.reqQ.put((node_uid, rvf, "SDR"))
            self.pending = True
            self.data_mode = True
        return True

    def __runloop_cb(self, node_uid, message):
        rvf = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
        rvf.UID = node_uid
        rvf.run_state = p2654model2.rvf.protocols.JTAG_pb2.IDLE_STABLE
        rvf.run_count = message.cycle_count
        if message.run_clk == p2654model2.rvf.protocols.SCAN_pb2.SCK:
            rvf.run_clk = "SCK"
        else:
            rvf.run_clk = "TCK"
        rvf.min_time = str(message.min_time)
        rvf.max_time = rvf.min_time
        # self.reqQ.append((node_uid, rvf, "RUNTEST"))
        self.reqQ.put((node_uid, rvf, "RUNTEST"))
        self.pending = True
        if message.UID == self.children_uids[0]:
            self.data_mode = False
        else:
            self.data_mode = True
        return True

    def __reset_cb(self, node_uid, message):
        rvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
        rvf.UID = node_uid
        rvf.state = True
        # self.reqQ.append((node_uid, rvf, "TRST"))
        self.reqQ.put((node_uid, rvf, "TRST"))
        rvf.state = False
        # self.reqQ.append((node_uid, rvf, "TRST"))
        self.reqQ.put((node_uid, rvf, "TRST"))
        self.pending = True
        if message.UID == self.children_uids[0]:
            self.data_mode = False
        else:
            self.data_mode = True
        return True

    def __endstate_cb(self, node_uid, message):
        if message.UID == self.children_uids[0]:  # The Instruction Register message
            rvf = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
            rvf.UID = node_uid
            self.stable_state = message.state
            if message.state == p2654model2.rvf.protocols.SCAN_pb2.NOP4_STABLE:
                rvf.state = p2654model2.rvf.protocols.JTAG_pb2.IRPAUSE_STABLE
            else:
                rvf.state = p2654model2.rvf.protocols.JTAG_pb2.IDLE_STABLE
            # self.reqQ.append((node_uid, rvf, "ENDIR"))
            self.reqQ.put((node_uid, rvf, "ENDIR"))
            self.pending = True
            self.data_mode = False
        else:  # DRMUX paths
            rvf = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
            rvf.UID = node_uid
            self.stable_state = message.state
            if message.state == p2654model2.rvf.protocols.SCAN_pb2.NOP4_STABLE:
                rvf.state = p2654model2.rvf.protocols.JTAG_pb2.DRPAUSE_STABLE
            else:
                rvf.state = p2654model2.rvf.protocols.JTAG_pb2.IDLE_STABLE
            # self.reqQ.append((node_uid, rvf, "ENDDR"))
            self.reqQ.put((node_uid, rvf, "ENDDR"))
            self.pending = True
            self.data_mode = True
        return True

    def __enddr_resp_cb(self, node_uid, message):
        rvf = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
        rvf.UID = self.children_uids[1]
        rvf.state = self.stable_state
        self.__sendResponse(node_uid, rvf, "ENDSTATE", self.children_uids[1])
        return True

    def __endir_resp_cb(self, node_uid, message):
        rvf = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
        rvf.UID = self.children_uids[0]
        rvf.state = self.stable_state
        self.__sendResponse(node_uid, rvf, "ENDSTATE", self.children_uids[0])
        return True

    def __sdr_resp_cb(self, node_uid, message):
        return self.__data_resp("SDR", node_uid, message)

    def __sir_resp_cb(self, node_uid, message):
        return self.__data_resp("SIR", node_uid, message)

    def __data_resp(self, metaname, node_uid, message):
        if self.command == "S":
            rvf = p2654model2.rvf.protocols.SCAN_pb2.S()
            for v in message.tdi:
                rvf.si_vector.append(v)
            for v in message.tdo:
                rvf.so_vector.append(v)
        elif self.command == "SU":
            rvf = p2654model2.rvf.protocols.SCAN_pb2.SU()
            for v in message.tdi:
                rvf.si_vector.append(v)
        elif self.command == "CS":
            rvf = p2654model2.rvf.protocols.SCAN_pb2.CS()
            for v in message.tdo:
                rvf.so_vector.append(v)
        else:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            for v in message.tdi:
                rvf.si_vector.append(v)
            for v in message.tdo:
                rvf.so_vector.append(v)
        if self.data_mode:
            uid = self.children_uids[1]
        else:
            uid = self.children_uids[0]
        self.__sendResponse(node_uid, rvf, self.command, uid)
        return True

    def __runtest_resp_cb(self, node_uid, message):
        rvf = p2654model2.rvf.protocols.SCAN_pb2.RUNLOOP()
        rvf.cycle_count = message.run_count
        if message.run_clk == "SCK":
            clk = p2654model2.rvf.protocols.SCAN_pb2.SCK
        else:
            clk = p2654model2.rvf.protocols.SCAN_pb2.TCK
        rvf.run_clk = clk
        rvf.min_time = int(message.min_time)
        if self.data_mode:
            uid = self.children_uids[1]
        else:
            uid = self.children_uids[0]
        self.__sendResponse(node_uid, rvf, "RUNLOOP", uid)
        return True

    def __trst_resp_cb(self, node_uid, message):
        rvf = p2654model2.rvf.protocols.SCAN_pb2.RESET()
        if self.data_mode:
            uid = self.children_uids[1]
        else:
            uid = self.children_uids[0]
        self.__sendResponse(node_uid, rvf, "RESET", uid)
        return True

    def __update_enddr_cb(self, node_uid, message):
        self.enddr = message.state
        return True

    def __update_endir_cb(self, node_uid, message):
        self.endir = message.state
        return True

    def __update_sdr_cb(self, node_uid, message):
        return self.__update_data_cb("SDR", node_uid, message)

    def __update_sir_cb(self, node_uid, message):
        return self.__update_data_cb("SIR", node_uid, message)

    def __update_data_cb(self, metaname, node_uid, message):
        tdi = self.ipint2int(message.tdi)
        tdo = self.ipint2int(message.tdo)
        mask = self.ipint2int(message.mask)
        nmetaname = None
        resp = None
        if metaname == "SIR":
            if self.endir == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.TLR_STABLE:
                nmetatname = "CSU"
                resp = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            elif self.endir == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.IDLE_STABLE:
                nmetatname = "CSU"
                resp = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            elif self.endir == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.DRPAUSE_STABLE:
                nmetatname = "S"
                resp = p2654model2.rvf.protocols.SCAN_pb2.S()
            elif self.endir == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.IRPAUSE_STABLE:
                nmetatname = "S"
                resp = p2654model2.rvf.protocols.SCAN_pb2.S()
        else:
            if self.enddr == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.TLR_STABLE:
                nmetatname = "CSU"
                resp = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            elif self.enddr == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.IDLE_STABLE:
                nmetatname = "CSU"
                resp = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            elif self.enddr == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.DRPAUSE_STABLE:
                nmetatname = "S"
                resp = p2654model2.rvf.protocols.SCAN_pb2.S()
            elif self.enddr == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.IRPAUSE_STABLE:
                nmetatname = "S"
                resp = p2654model2.rvf.protocols.SCAN_pb2.S()
        start = 0
        end = 0
        i = 0
        for uid in self.children_uids:
            nrbits = len(self.tdi[i])
            end = nrbits + end
            resp.UID = uid
            resp.si_vector = self.__vector_to_list(nrbits, intbv(tdi[start:end]))
            resp.so_vector = self.__vector_to_list(nrbits, intbv(tdo[start:end]))
            resp.nrbits = nrbits
            self.__updateRequest(node_uid, resp, metaname, uid)
            start = end
            i += 1
        self.__updateDataValue(node_uid, message.tdo)
        return True

    def __update_runtest_cb(self, node_uid, message):
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.RUNLOOP()
            rvf.UID = uid
            rvf.cycle_count = message.run_count
            if message.run_clk == "SCK":
                rvf.run_clk = p2654model2.rvf.protocols.SCAN_pb2.SCK
            else:
                rvf.run_clk = p2654model2.rvf.protocols.SCAN_pb2.TCK
            rvf.min_time = message.min_time
            self.__updateRequest(node_uid, rvf, "RUNLOOP", uid)
        return True

    def __update_trst_cb(self, node_uid, message):
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.RESET()
            rvf.UID = uid
            self.__updateRequest(node_uid, rvf, "RESET", uid)
        return True

    def __update_state_cb(self, node_uid, message):
        return True

    def __update_frequency_cb(self, node_uid, message):
        return True

    def __update_enddr_resp_cb(self, node_uid, message):
        self.enddr = message.state
        return True

    def __update_endir_resp_cb(self, node_uid, message):
        self.endir = message.state
        return True

    def __update_sdr_resp_cb(self, node_uid, message):
        return self.__update_data_resp_cb("SDR", node_uid, message)

    def __update_sir_resp_cb(self, node_uid, message):
        return self.__update_data_resp_cb("SIR", node_uid, message)

    def __update_data_resp_cb(self, metaname, node_uid, message):
        tdi = self.ipint2int(message.tdi)
        tdo = self.ipint2int(message.tdo)
        mask = self.ipint2int(message.mask)
        nmetaname = None
        resp = None
        if metaname == "SIR":
            if self.endir == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.TLR_STABLE:
                nmetatname = "CSU"
                resp = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            elif self.endir == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.IDLE_STABLE:
                nmetatname = "CSU"
                resp = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            elif self.endir == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.DRPAUSE_STABLE:
                nmetatname = "S"
                resp = p2654model2.rvf.protocols.SCAN_pb2.S()
            elif self.endir == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.IRPAUSE_STABLE:
                nmetatname = "S"
                resp = p2654model2.rvf.protocols.SCAN_pb2.S()
        else:
            if self.enddr == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.TLR_STABLE:
                nmetatname = "CSU"
                resp = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            elif self.enddr == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.IDLE_STABLE:
                nmetatname = "CSU"
                resp = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            elif self.enddr == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.DRPAUSE_STABLE:
                nmetatname = "S"
                resp = p2654model2.rvf.protocols.SCAN_pb2.S()
            elif self.enddr == p2654model2.rvf.protocols.JTAG_pb2.SVFStableState.IRPAUSE_STABLE:
                nmetatname = "S"
                resp = p2654model2.rvf.protocols.SCAN_pb2.S()
        start = 0
        end = 0
        i = 0
        for uid in self.children_uids:
            nrbits = len(self.tdi[i])
            end = nrbits + end
            resp.UID = uid
            resp.si_vector = self.__vector_to_list(nrbits, intbv(tdi[start:end]))
            resp.so_vector = self.__vector_to_list(nrbits, intbv(tdo[start:end]))
            resp.nrbits = nrbits
            self.__updateResponse(node_uid, resp, metaname, uid)
            start = end
            i += 1
        self.__updateDataValue(node_uid, message.tdo)
        return True

    def __update_runtest_resp_cb(self, node_uid, message):
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.RUNLOOP()
            rvf.UID = uid
            rvf.cycle_count = message.run_count
            if message.run_clk == "SCK":
                rvf.run_clk = p2654model2.rvf.protocols.SCAN_pb2.SCK
            else:
                rvf.run_clk = p2654model2.rvf.protocols.SCAN_pb2.TCK
            rvf.min_time = message.min_time
            self.__updateResponse(node_uid, rvf, "RUNLOOP", uid)
        return True

    def __update_trst_resp_cb(self, node_uid, message):
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.RESET()
            rvf.UID = uid
            self.__updateResponse(node_uid, rvf, "RESET", uid)
        return True

    def __update_state_resp_cb(self, node_uid, message):
        return True

    def __update_frequency_resp_cb(self, node_uid, message):
        return True

    def __sendRequest(self, node_uid, message, metaname):
        self.logger.debug("TAPTransform.__sendRequest({:s}): sending {:s} RVF\n".format(self.name, metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = self.node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendRequestCallback(node_uid, wrapper)

    def __sendResponse(self, node_uid, message, metaname, uid):
        self.logger.debug("TAPTransform.__sendResponse({:s}): sending {:s} RVF\n".format(self.name, metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendResponseCallback(node_uid, wrapper)

    def __updateRequest(self, node_uid, message, metaname, uid):
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = self.node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.updateRequestCallback(node_uid, wrapper)

    def __updateResponse(self, node_uid, message, metaname, uid):
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.updateResponseCallback(node_uid, wrapper)

    def __updateDataValue(self, node_uid, tdo):
        self.logger.debug("TAPTransform.__updateDataValue({:s}):\n".format(self.name))
        dvmsg = p2654model2.rvf.rvfmessage_pb2.RVFDataValue()
        dvmsg.UID = node_uid
        for v in tdo:
            dvmsg.data.append(v)
        return self.updateDataValueCallback(node_uid, dvmsg)

    def set_sendRequestCallback(self, callback):
        self.sendRequestCallback = callback

    def set_sendResponseCallback(self, callback):
        self.sendResponseCallback = callback

    def set_updateRequestCallback(self, callback):
        self.updateRequestCallback = callback

    def set_updateResponseCallback(self, callback):
        self.updateResponseCallback = callback

    def set_updateDataValueCallback(self, callback):
        self.updateDataValueCallback = callback

    def set_registerObserverCallback(self, callback):
        self.registerObserverCallback = callback

    def set_sendObserverCallback(self, callback):
        self.sendObserverCallback = callback

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

    def indent(self):
        self.__indent += 4

    def dedent(self):
        self.__indent -= 4

    def writeln(self, ln):
        print(" " * self.__indent, ln)

    def dump(self, indent):
        self.__indent = indent
        self.writeln("Dumping TAPTransform: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("child_uid = {:s}".format(str(self.child_uid)))
        self.writeln("params = {:s}".format(str(self.params)))
        self.writeln("children_uids = {:s}".format(str(self.children_uids)))
        self.writeln("command = {:s}".format(str(self.command)))
        self.dedent()
