#!/usr/bin/env python
"""
    Specialized Transformation Strategy for TAP Data Register LINKERs.
    Copyright (C) 2021  Bradford G. Van Treuren

    Specialized Transformation Strategy for TAP Data Register LINKERs.
    This strategy is implemented as a built-in plug-in module wrapped by its own TransformationStrategy
    instance.  To use this strategy, specify the name TAPMux as the "tstrategy"
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
import p2654model2.rvf.protocols.SCAN_pb2
import p2654model2.rvf.protocols.JTAG_pb2
import p2654model2.rvf.rvfmessage_pb2
from queue import Queue
import ast

import logging
from autologging import traced, logged

module_logger = logging.getLogger('p2654model2.strategy.transforms.strategies.TAPMux')


@logged
@traced
class TAPMux(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('p2654model2.strategy.transforms.strategies.TAPMux')
        self.logger.info('Creating an instance of TAPMux')
        self.name = None
        self.node_uid = None
        self.child_uid = None
        self.children_uids = None
        self.children_names = None
        self.selections = []
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
        self.selector = None
        self.derivations = None
        self.control = None
        self.selkeys = []
        self.selvals = []

    def create(self, name, node_uid, children_uids, children_names, params):
        # print("TAPMux params = {:s}".format(params))
        self.name = name
        self.node_uid = node_uid
        self.children_uids = children_uids
        self.children_names = children_names
        if len(self.children_uids):
            self.selections = [False for _ in range(len(self.children_uids))]
        else:
            self.selections = []
        self.params = params
        return None

    def configure(self):
        return self.__parse_parameters()


    def handleRequest(self, node_uid, message):
        self.logger.debug("TAPMux.handleRequest(): processing {:s} RVF\n".format(message.metaname))
        print("TAPMux handling request ({:s}).".format(message.metaname))
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
        self.logger.debug("TAPMux.handleResponse(): processing {:s} RVF\n".format(message.metaname))
        print("TAPMux handling response ({:s}).".format(message.metaname))
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
        elif message.metaname == "SU":
            s = p2654model2.rvf.protocols.SCAN_pb2.SU()
            s.ParseFromString(message.serialized)
            return self.__su_resp_cb(node_uid, s)
        elif message.metaname == "CS":
            s = p2654model2.rvf.protocols.SCAN_pb2.CS()
            s.ParseFromString(message.serialized)
            return self.__cs_resp_cb(node_uid, s)
        elif message.metaname == "CSU":
            s = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            s.ParseFromString(message.serialized)
            return self.__csu_resp_cb(node_uid, s)
        elif message.metaname == "S":
            s = p2654model2.rvf.protocols.SCAN_pb2.S()
            s.ParseFromString(message.serialized)
            return self.__s_resp_cb(node_uid, s)
        elif message.metaname == "RUNLOOP":
            s = p2654model2.rvf.protocols.SCAN_pb2.RUNLOOP()
            s.ParseFromString(message.serialized)
            return self.__runloop_resp_cb(node_uid, s)
        elif message.metaname == "RESET":
            s = p2654model2.rvf.protocols.SCAN_pb2.RESET()
            s.ParseFromString(message.serialized)
            return self.__reset_resp_cb(node_uid, s)
        elif message.metaname == "ENDSTATE":
            s = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
            s.ParseFromString(message.serialized)
            return self.__endstate_resp_cb(node_uid, s)
        return None

    def updateRequest(self, node_uid, message):
        self.logger.debug("TAPMux.updateRequest(): processing {:s} RVF\n".format(message.metaname))
        self.status_message = "OK"
        self.status_code = 0
        self.error_message = "UNKNOWN"
        self.error_code = 0
        if message.metaname == "SU":
            s = p2654model2.rvf.protocols.SCAN_pb2.SU()
            s.ParseFromString(message.serialized)
            return self.__su_update_cb(node_uid, s)
        elif message.metaname == "CS":
            s = p2654model2.rvf.protocols.SCAN_pb2.CS()
            s.ParseFromString(message.serialized)
            return self.__cs_update_cb(node_uid, s)
        elif message.metaname == "CSU":
            s = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            s.ParseFromString(message.serialized)
            return self.__csu_update_cb(node_uid, s)
        elif message.metaname == "S":
            s = p2654model2.rvf.protocols.SCAN_pb2.S()
            s.ParseFromString(message.serialized)
            return self.__s_update_cb(node_uid, s)
        elif message.metaname == "RUNLOOP":
            s = p2654model2.rvf.protocols.SCAN_pb2.RUNLOOP()
            s.ParseFromString(message.serialized)
            return self.__runloop_update_cb(node_uid, s)
        elif message.metaname == "RESET":
            s = p2654model2.rvf.protocols.SCAN_pb2.RESET()
            s.ParseFromString(message.serialized)
            return self.__reset_update_cb(node_uid, s)
        elif message.metaname == "ENDSTATE":
            s = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
            s.ParseFromString(message.serialized)
            return self.__endstate_update_cb(node_uid, s)
        return None

    def updateResponse(self, node_uid, message):
        self.logger.debug("TAPMux.updateResponse(): processing {:s} RVF\n".format(message.metaname))
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

    def update_observer(self, node_id, message):
        # Message type is an RVFSelectEvent
        # Only the IR as a single selector for TAPMux
        ir_value = intbv(TAPMux.ipint2int(message.data))
        i = 0
        for k in self.selkeys:
            if k == ir_value:
                v = self.selvals[i]
                j = 0
                for c in self.children_names:
                    if c == v:
                        for x in range(0, len(self.children_uids)):
                            self.deselect(x)
                        self.select(j)
                        return True
                    j += 1
            i += 1
        raise AssertionError("Invalid code given to IR ({:s}).".format(hex(ir_value)))
        # return False

    def select(self, index):
        self.selections[index] = True

    def deselect(self, index):
        self.selections[index] = False

    def getStatus(self, node_uid, timeout):
        print("TAPMux getStatus ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.STATUS
        rvf.message = "OK"
        rvf.code = 0
        return rvf

    def getError(self, node_uid, timeout):
        print("TAPMux getError ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFError()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.ERROR
        rvf.message = "UNKNOWN"
        rvf.code = 0
        return rvf

    def apply(self, node_uid, timeout=0):
        self.logger.debug("TAPMux.apply(): processing {:d} node_uid\n".format(node_uid))
        print("TAPMux apply()")
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
        return ["CSU", "SU", "CS", "S", "RUNLOOP", "RESET", "ENDSTATE", "SELECT", "DESELECT"]

    def destroy(self, node_uid):
        return None

    def __su_cb(self, node_uid, message):
        self.command = "SU"
        self.child_uid = message.UID
        i = 0
        for uid in self.children_uids:
            if uid == message.UID:
                break
            i += 1
        self.logger.debug("TAPMux.__su_cb(): i={:d}, node_uid={:d}, selections={:s}\n".format(i, node_uid, str(self.selections)))
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.SU()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.si_vector:
                rvf.si_vector.append(v)
            self.pending = True
            self.data_mode = False
            # self.reqQ.append((node_uid, rvf, "SU"))
            self.reqQ.put((node_uid, rvf, "SU"))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __cs_cb(self, node_uid, message):
        self.command = "CS"
        self.child_uid = message.UID
        i = 0
        for uid in self.children_uids:
            if uid == message.UID:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.CS()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.so_vector:
                rvf.so_vector.append(v)
            self.__updateDataValue(node_uid, message)
            self.pending = True
            self.data_mode = False
            # self.reqQ.append((node_uid, rvf, "CS"))
            self.reqQ.put((node_uid, rvf, "CS"))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __csu_cb(self, node_uid, message):
        self.command = "CSU"
        self.child_uid = message.UID
        i = 0
        for uid in self.children_uids:
            if uid == message.UID:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.si_vector:
                rvf.si_vector.append(v)
            for v in message.so_vector:
                rvf.so_vector.append(v)
            self.__updateDataValue(node_uid, message)
            self.pending = True
            self.data_mode = False
            # self.reqQ.append((node_uid, rvf, "CSU"))
            self.reqQ.put((node_uid, rvf, "CSU"))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __s_cb(self, node_uid, message):
        self.command = "S"
        self.child_uid = message.UID
        i = 0
        for uid in self.children_uids:
            if uid == message.UID:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.S()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.si_vector:
                rvf.si_vector.append(v)
            for v in message.so_vector:
                rvf.so_vector.append(v)
            self.__updateDataValue(node_uid, message)
            self.pending = True
            self.data_mode = False
            # self.reqQ.append((node_uid, rvf, "S"))
            self.reqQ.put((node_uid, rvf, "S"))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __runloop_cb(self, node_uid, message):
        self.command = "RUNLOOP"
        self.child_uid = message.UID
        i = 0
        for uid in self.children_uids:
            if uid == message.UID:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.RUNLOOP()
            rvf.UID = node_uid
            rvf.cycle_count = message.cycle_count
            rvf.run_clk = message.run_clk
            rvf.min_time = message.min_time
            self.pending = True
            self.data_mode = False
            # self.reqQ.append((node_uid, rvf, "RUNLOOP"))
            self.reqQ.put((node_uid, rvf, "RUNLOOP"))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __reset_cb(self, node_uid, message):
        self.command = "RESET"
        self.child_uid = message.UID
        i = 0
        for uid in self.children_uids:
            if uid == message.UID:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.RESET()
            rvf.UID = node_uid
            self.pending = True
            self.data_mode = False
            # self.reqQ.append((node_uid, rvf, "RESET"))
            self.reqQ.put((node_uid, rvf, "RESET"))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __endstate_cb(self, node_uid, message):
        self.command = "ENDSTATE"
        self.child_uid = message.UID
        i = 0
        for uid in self.children_uids:
            if uid == message.UID:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
            rvf.UID = node_uid
            rvf.state = message.state
            self.pending = True
            self.data_mode = False
            # self.reqQ.append((node_uid, rvf, "ENDSTATE"))
            self.reqQ.put((node_uid, rvf, "ENDSTATE"))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __su_resp_cb(self, node_uid, message):
        self.command = "SU"
        i = 0
        for uid in self.children_uids:
            if uid == self.child_uid:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.SU()
            rvf.UID = self.child_uid
            rvf.nrbits = message.nrbits
            for v in message.si_vector:
                rvf.si_vector.append(v)
            # self.respQ.append((node_uid, rvf, "SU", self.child_uid))
            self.respQ.put((node_uid, rvf, "SU", self.child_uid))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __cs_resp_cb(self, node_uid, message):
        self.command = "CS"
        i = 0
        for uid in self.children_uids:
            if uid == self.child_uid:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.CS()
            rvf.UID = self.child_uid
            rvf.nrbits = message.nrbits
            for v in message.so_vector:
                rvf.so_vector.append(v)
            self.__updateDataValue(node_uid, message)
            # self.respQ.append((node_uid, rvf, "CS", self.child_uid))
            self.respQ.put((node_uid, rvf, "CS", self.child_uid))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __csu_resp_cb(self, node_uid, message):
        self.command = "CSU"
        i = 0
        for uid in self.children_uids:
            if uid == self.child_uid:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.si_vector:
                rvf.si_vector.append(v)
            for v in message.so_vector:
                rvf.so_vector.append(v)
            self.__updateDataValue(node_uid, message)
            # self.respQ.append((node_uid, rvf, "CSU", self.child_uid))
            self.respQ.put((node_uid, rvf, "CSU", self.child_uid))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __s_resp_cb(self, node_uid, message):
        self.command = "S"
        i = 0
        for uid in self.children_uids:
            if uid == self.child_uid:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.S()
            rvf.UID = node_uid
            rvf.nrbits = message.nrbits
            for v in message.si_vector:
                rvf.si_vector.append(v)
            for v in message.so_vector:
                rvf.so_vector.append(v)
            self.__updateDataValue(node_uid, message)
            # self.respQ.append((node_uid, rvf, "S", self.child_uid))
            self.respQ.put((node_uid, rvf, "S", self.child_uid))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __runloop_resp_cb(self, node_uid, message):
        self.command = "RUNLOOP"
        i = 0
        for uid in self.children_uids:
            if uid == self.child_uid:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.RUNLOOP()
            rvf.UID = node_uid
            rvf.cycle_count = message.cycle_count
            rvf.run_clk = message.run_clk
            rvf.min_time = message.min_time
            # self.respQ.append((node_uid, rvf, "RUNLOOP", self.child_uid))
            self.respQ.put((node_uid, rvf, "RUNLOOP", self.child_uid))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __reset_resp_cb(self, node_uid, message):
        self.command = "RESET"
        i = 0
        for uid in self.children_uids:
            if uid == self.child_uid:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.RESET()
            rvf.UID = node_uid
            # self.respQ.append((node_uid, rvf, "RESET", self.child_uid))
            self.respQ.put((node_uid, rvf, "RESET", self.child_uid))
        else:
            raise AssertionError("Path not selected.")
        return True

    def __endstate_resp_cb(self, node_uid, message):
        self.command = "ENDSTATE"
        i = 0
        for uid in self.children_uids:
            if uid == self.child_uid:
                break
            i += 1
        if self.selections[i]:
            rvf = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
            rvf.UID = node_uid
            rvf.state = message.state
            # self.respQ.append((node_uid, rvf, "ENDSTATE", self.child_uid))
            self.respQ.put((node_uid, rvf, "ENDSTATE", self.child_uid))
        else:
            raise AssertionError("Path not selected.")
        return True

    # def __update_enddr_cb(self, node_uid, message):
    #     for uid in self.children_uids:
    #         rvf = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
    #         rvf.UID = uid
    #         rvf.state = message.state
    #         self.__updateRequest(node_uid, rvf, "ENDDR", uid)
    #     return True
    #
    # def __update_endir_cb(self, node_uid, message):
    #     for uid in self.children_uids:
    #         rvf = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
    #         rvf.UID = uid
    #         rvf.state = message.state
    #         self.__updateRequest(node_uid, rvf, "ENDIR", uid)
    #     return True
    #
    # def __update_sdr_cb(self, node_uid, message):
    #     return self.__update_data_cb("SDR", node_uid, message)
    #
    # def __update_sir_cb(self, node_uid, message):
    #     return self.__update_data_cb("SIR", node_uid, message)
    #
    # def __update_data_cb(self, metaname, node_uid, message):
    #     tdi = self.ipint2int(message.tdi)
    #     tdo = self.ipint2int(message.tdo)
    #     mask = self.ipint2int(message.mask)
    #     start = 0
    #     end = 0
    #     i = 0
    #     for uid in self.children_uids:
    #         nrbits = len(self.tdi[i])
    #         end = nrbits + end
    #         if metaname == "SIR":
    #             resp = p2654model2.rvf.protocols.JTAG_pb2.SIR()
    #         else:
    #             resp = p2654model2.rvf.protocols.JTAG_pb2.SDR()
    #         resp.UID = uid
    #         resp.tdi = self.__vector_to_list(nrbits, intbv(tdi[start:end]))
    #         resp.tdo = self.__vector_to_list(nrbits, intbv(tdo[start:end]))
    #         resp.mask = self.__vector_to_list(nrbits, intbv(mask[start:end]))
    #         resp.nrbits = nrbits
    #         self.__updateRequest(node_uid, resp, metaname, uid)
    #         start = end
    #         i += 1
    #     return True
    #
    # def __update_runtest_cb(self, node_uid, message):
    #     for uid in self.children_uids:
    #         rvf = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
    #         rvf.UID = uid
    #         rvf.run_state = message.run_state
    #         rvf.run_count = message.run_count
    #         rvf.run_clk = message.run_clk
    #         rvf.min_time = message.min_time
    #         rvf.max_time = message.max_time
    #         rvf.end_state = message.end_state
    #         self.__updateRequest(node_uid, rvf, "RUNTEST", uid)
    #     return True
    #
    # def __update_trst_cb(self, node_uid, message):
    #     for uid in self.children_uids:
    #         rvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
    #         rvf.UID = uid
    #         rvf.state = message.state
    #         self.__updateRequest(node_uid, rvf, "TRST", uid)
    #     return True
    #
    # def __update_state_cb(self, node_uid, message):
    #     for uid in self.children_uids:
    #         rvf = p2654model2.rvf.protocols.JTAG_pb2.STATE()
    #         rvf.UID = uid
    #         for s in self.state_message.state:
    #             rvf.state.append(s)
    #         rvf.end_state = self.state_message.end_state
    #         self.__updateRequest(node_uid, rvf, "STATE", uid)
    #     return True
    #
    # def __update_frequency_cb(self, node_uid, message):
    #     for uid in self.children_uids:
    #         rvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
    #         rvf.UID = uid
    #         rvf.cycles = message.cycles
    #         self.__updateRequest(node_uid, rvf, "FREQUENCY", uid)
    #     return True
    #
    # def __update_enddr_resp_cb(self, node_uid, message):
    #     for uid in self.children_uids:
    #         rvf = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
    #         rvf.UID = uid
    #         rvf.state = message.state
    #         self.__updateResponse(node_uid, rvf, "ENDDR", uid)
    #     return True
    #
    # def __update_endir_resp_cb(self, node_uid, message):
    #     for uid in self.children_uids:
    #         rvf = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
    #         rvf.UID = uid
    #         rvf.state = message.state
    #         self.__updateResponse(node_uid, rvf, "ENDIR", uid)
    #     return True
    #
    # def __update_sdr_resp_cb(self, node_uid, message):
    #     return self.__update_data_resp_cb("SDR", node_uid, message)
    #
    # def __update_sir_resp_cb(self, node_uid, message):
    #     return self.__update_data_resp_cb("SIR", node_uid, message)
    #
    # def __update_data_resp_cb(self, metaname, node_uid, message):
    #     start = 0
    #     end = 0
    #     i = 0
    #     for uid in self.children_uids:
    #         end = len(self.tdi[i]) + end
    #         if metaname == "SIR":
    #             resp = p2654model2.rvf.protocols.JTAG_pb2.SIR()
    #         else:
    #             resp = p2654model2.rvf.protocols.JTAG_pb2.SDR()
    #         resp.UID = uid
    #         nrbits = len(intbv(self.tdi[i][start:end]))
    #         resp.tdi = self.__vector_to_list(nrbits, intbv(self.tdi[i][start:end]))
    #         resp.tdo = self.__vector_to_list(nrbits, intbv(self.tdo[i][start:end]))
    #         resp.mask = self.__vector_to_list(nrbits, intbv(self.mask[i][start:end]))
    #         resp.nrbits = nrbits
    #         self.__updateResponse(node_uid, resp, metaname, uid)
    #         start = end
    #         i += 1
    #     return True
    #
    # def __update_runtest_resp_cb(self, node_uid, message):
    #     for uid in self.children_uids:
    #         rvf = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
    #         rvf.UID = uid
    #         rvf.run_state = message.run_state
    #         rvf.run_count = message.run_count
    #         rvf.run_clk = message.run_clk
    #         rvf.min_time = message.min_time
    #         rvf.max_time = message.max_time
    #         rvf.end_state = message.end_state
    #         self.__updateResponse(node_uid, rvf, "RUNTEST", uid)
    #     return True
    #
    # def __update_trst_resp_cb(self, node_uid, message):
    #     for uid in self.children_uids:
    #         rvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
    #         rvf.UID = uid
    #         rvf.state = message.state
    #         self.__updateResponse(node_uid, rvf, "TRST", uid)
    #     return True
    #
    # def __update_state_resp_cb(self, node_uid, message):
    #     for uid in self.children_uids:
    #         rvf = p2654model2.rvf.protocols.JTAG_pb2.STATE()
    #         rvf.UID = uid
    #         for s in self.state_message.state:
    #             rvf.state.append(s)
    #         rvf.end_state = self.state_message.end_state
    #         self.__updateResponse(node_uid, rvf, "STATE", uid)
    #     return True
    #
    # def __update_frequency_resp_cb(self, node_uid, message):
    #     for uid in self.children_uids:
    #         rvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
    #         rvf.UID = uid
    #         rvf.cycles = message.cycles
    #         self.__updateResponse(node_uid, rvf, "FREQUENCY", uid)
    #     return True

    def __sendRequest(self, node_uid, message, metaname):
        self.logger.debug("TAPMux.__sendRequest(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = self.node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendRequestCallback(node_uid, wrapper)

    def __sendResponse(self, node_uid, message, metaname, uid):
        self.logger.debug("TAPMux.__sendResponse(): sending {:s} RVF\n".format(metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendResponseCallback(node_uid, wrapper)

    def __updateDataValue(self, node_uid, message):
        self.logger.debug("TAPMux.__updateDataValue():\n")
        dvmmsg = p2654model2.rvf.rvfmessage_pb2.RVFDataValue()
        dvmmsg.UID = node_uid
        dvmmsg.nrbits = message.nrbits
        for v in message.so_vector:
            dvmmsg.data.append(v)
        return self.updateDataValueCallback(node_uid, dvmmsg)

    # def __updateRequest(self, node_uid, message, metaname, uid):
    #     wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
    #     wrapper.UID = self.node_uid
    #     wrapper.metaname = metaname
    #     wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
    #     wrapper.serialized = message.SerializeToString()
    #     return self.updateRequestCallback(node_uid, wrapper)
    #
    # def __updateResponse(self, node_uid, message, metaname, uid):
    #     wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
    #     wrapper.UID = uid
    #     wrapper.metaname = metaname
    #     wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
    #     wrapper.serialized = message.SerializeToString()
    #     return self.updateResponseCallback(node_uid, wrapper)

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

    # def set_updateRequestCallback(self, callback):
    #     self.updateRequestCallback = callback
    #
    # def set_updateResponseCallback(self, callback):
    #     self.updateResponseCallback = callback

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
        logger = logging.getLogger('p2654model2.strategy.transforms.strategies.TAPMux')
        v = 0
        i = 0
        for n in val:
            logger.debug("TAPMux.ipint2int(): val = {:s}, v = {:d}, n = {:d}, i = {:d}, (n << (i * 32) = {:d}\n".format(str(val), v, n, i, (n << (i * 32))))
            v = v + (n << (i * 32))
            i += 1
        return v

    def __parse_parameters(self):
        args, kwargs = self.__parse_params(self.params)
        for k, v in kwargs.items():
            if k == "selector":
                self.__setup_selector(v)
            elif k == "derivations":
                self.__setup_derivations(v)
            elif k == "control":
                self.__setup_control(v)
            else:
                raise AssertionError("Invalid parameter detected!")
        return True

    def __setup_selector(self, v):
        """
        TBD - Ideally, the selector coding and decoding should be done in model native language and
        only select and deselect calls with index to the specific transform strategy extension code.
        """
        try:
            self.selector = v["Table"][0]
            self.logger.debug("TAPMux.__setup_selector(): self.selector {:s}\n".format(str(self.selector)))
            self.logger.debug("TAPMux.__setup_selector(): self.selector type {:s}\n".format(str(type(self.selector))))
            for k, v in self.selector.items():
                if "0x" in k:
                    self.selkeys.append(intbv(int(k, 16)))
                elif "0o" in k:
                    self.selkeys.append(intbv(int(k, 8)))
                elif "0b" in k:
                    self.selkeys.append(intbv(k))
                else:
                    self.selkeys.append(intbv(int(k)))
                self.selvals.append(v)
        except KeyError:
            raise AssertionError("Invalid selector type detected! Need a Table specification for TAPMux.")

    def __setup_derivations(self, v):
        self.derivations = v
        self.logger.debug("TAPMux.__setup_derivations(): self.derivations {:s}\n".format(str(self.derivations)))

    def __setup_control(self, v):
        self.control = v
        self.logger.debug("TAPMux.__setup_control(): self.control {:s}\n".format(str(self.control)))
        self.registerObserverCallback(self.node_uid, self.control)

    def __parse_params(self, args):
        args = 'f({})'.format(args)
        tree = ast.parse(args)
        funccall = tree.body[0].value

        args = [ast.literal_eval(arg) for arg in funccall.args]
        kwargs = {arg.arg: ast.literal_eval(arg.value) for arg in funccall.keywords}
        return args, kwargs

    # def __parse_params(self, s):
    #     data = {"kwargs": {}, "args": []}
    #     params = s.split(" ")
    #     for item in params:
    #         if "=" in item:
    #             k = item.split("=")
    #             data['kwargs'][k[0]] = k[1]
    #         else:
    #             data['args'].append(item)
    #     return data
    #
    def indent(self):
        self.__indent += 4

    def dedent(self):
        self.__indent -= 4

    def writeln(self, ln):
        print(" " * self.__indent, ln)

    def dump(self, indent):
        self.__indent = indent
        self.writeln("Dumping TAPMux: {:s}".format(str(self.name)))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("child_uid = {:s}".format(str(self.child_uid)))
        self.writeln("params = {:s}".format(str(self.params)))
        self.writeln("children_uids = {:s}".format(str(self.children_uids)))
        self.writeln("command = {:s}".format(str(self.command)))
        self.writeln("selector = {:s}".format(str(self.selector)))
        self.writeln("derivations = {:s}".format(str(self.derivations)))
        self.dedent()
