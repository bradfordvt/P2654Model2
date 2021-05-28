#!/usr/bin/env python
"""
    Specialized Transformation Strategy for JTAG CHAINs.
    Copyright (C) 2021  Bradford G. Van Treuren

    Specialized Transformation Strategy for JTAG CHAINs.
    This strategy is implemented as a built-in plug-in module wrapped by its own TransformationStrategy
    instance.  To use this strategy, specify the name JTAGChain as the "tstrategy"
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
import p2654model2.rvf.rvfmessage_pb2
from p2654model2.error.ModelError import ModelError

import logging
from autologging import traced, logged


module_logger = logging.getLogger('p2654model2.strategy.transforms.strategies.JTAGChain')


@logged
@traced
class JTAGChain(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('p2654model2.strategy.transforms.strategies.JTAGChain')
        self.logger.info('Creating an instance of JTAGChain')
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

    def create(self, name, node_uid, children_uids, children_names, params):
        # print("JTAGChain params = {:s}".format(str(params)))
        self.name = name
        self.node_uid = node_uid
        self.children_uids = children_uids
        self.children_names = children_names
        self.params = params
        return None

    def configure(self):
        return True

    def handleRequest(self, node_uid, message):
        self.logger.debug("JTAGChain.handleRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        print("JTAGChain handling request ({:s}).".format(message.metaname))
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
        self.logger.debug("JTAGChain.handleResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        print("TDRTransform handling response ({:s}).".format(message.metaname))
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

    # def updateRequest(self, node_uid, message):
    #     self.logger.debug("JTAGChain.updateRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
    #     if message.metaname == "ENDDR":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_enddr_cb(node_uid, s)
    #     elif message.metaname == "ENDIR":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_endir_cb(node_uid, s)
    #     elif message.metaname == "SDR":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.SDR()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_sdr_cb(node_uid, s)
    #     elif message.metaname == "SIR":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.SIR()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_sir_cb(node_uid, s)
    #     elif message.metaname == "RUNTEST":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_runtest_cb(node_uid, s)
    #     elif message.metaname == "TRST":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.TRST()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_trst_cb(node_uid, s)
    #     elif message.metaname == "STATE":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.STATE()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_state_cb(node_uid, s)
    #     elif message.metaname == "FREQUENCY":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.FREQUENCY()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_frequency_cb(node_uid, s)
    #     return 0
    #
    # def updateResponse(self, node_uid, message):
    #     self.logger.debug("JTAGChain.updateResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
    #     if message.metaname == "ENDDR":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_enddr_resp_cb(node_uid, s)
    #     elif message.metaname == "ENDIR":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_endir_resp_cb(node_uid, s)
    #     elif message.metaname == "SDR":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.SDR()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_sdr_resp_cb(node_uid, s)
    #     elif message.metaname == "SIR":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.SIR()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_sir_resp_cb(node_uid, s)
    #     elif message.metaname == "RUNTEST":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_runtest_resp_cb(node_uid, s)
    #     elif message.metaname == "TRST":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.TRST()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_trst_resp_cb(node_uid, s)
    #     elif message.metaname == "STATE":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.STATE()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_state_resp_cb(node_uid, s)
    #     elif message.metaname == "FREQUENCY":
    #         s = p2654model2.rvf.protocols.JTAG_pb2.FREQUENCY()
    #         s.ParseFromString(message.serialized)
    #         return self.__update_frequency_resp_cb(node_uid, s)
    #     return 0

    def getStatus(self, node_uid, timeout):
        print("TDRTransform getStatus ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.STATUS
        rvf.message = "OK"
        rvf.code = 0
        return rvf

    def getError(self, node_uid, timeout):
        print("TDRTransform getError ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFError()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.ERROR
        rvf.message = "UNKNOWN"
        rvf.code = 0
        return rvf

    def apply(self, node_uid, timeout=0):
        self.logger.debug("JTAGChain.apply({:s}): processing {:d} node_uid\n".format(self.name, node_uid))
        print("JTAGChainTransform apply()")
        pending = 0
        err = 0
        if not self.cached:
            self.__init_segments()
            self.cached = True
        if self.pending:
            if self.data_mode is None:
                raise ModelError("Pending conflict with data_mode!")
            if self.runtest_message is not None:
                wrvf = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
                wrvf.UID = node_uid
                wrvf.run_state = self.runtest_message.run_state
                wrvf.run_count = self.runtest_message.run_count
                wrvf.run_clk = self.runtest_message.run_clk
                wrvf.min_time = self.runtest_message.min_time
                wrvf.max_time = self.runtest_message.max_time
                wrvf.end_state = self.runtest_message.end_state
                pending += 1
                ret = self.__sendRequest(node_uid, wrvf, "RUNTEST")
                if not ret:
                    err += 1
                self.runtest_message = None
            if self.trst_message is not None:
                wrvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
                wrvf.UID = node_uid
                wrvf.state = self.trst_message.state
                pending += 1
                ret = self.__sendRequest(node_uid, wrvf, "TRST")
                if not ret:
                    err += 1
                self.trst_message = None
            if self.state_message is not None:
                wrvf = p2654model2.rvf.protocols.JTAG_pb2.STATE()
                wrvf.UID = node_uid
                for s in self.state_message.state:
                    wrvf.state.append(s)
                wrvf.end_state = self.state_message.end_state
                pending += 1
                ret = self.__sendRequest(node_uid, wrvf, "STATE")
                if not ret:
                    err += 1
                self.state_message = None
            if self.frequency_message is not None:
                wrvf = p2654model2.rvf.protocols.JTAG_pb2.FREQUENCY()
                wrvf.UID = node_uid
                wrvf.cycles = self.frequency_message.cycles
                pending += 1
                ret = self.__sendRequest(node_uid, wrvf, "FREQUENCY")
                if not ret:
                    err += 1
                self.frequency_message = None
            if self.enddr is not None:
                wrvf = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
                wrvf.UID = node_uid
                wrvf.state = self.enddr
                pending += 1
                ret = self.__sendRequest(node_uid, wrvf, "ENDDR")
                if not ret:
                    err += 1
                self.enddr = None
            if self.endir is not None:
                wrvf = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
                wrvf.UID = node_uid
                wrvf.state = self.endir
                pending += 1
                ret = self.__sendRequest(node_uid, wrvf, "ENDIR")
                if not ret:
                    err += 1
                self.endir = None
            if self.capture and self.data_mode:
                # Concatenate vectors together into a single vector to scan
                if len(self.tdi) > 1:
                    tdi = concat([v for v in self.tdi])
                    tdo = concat([v for v in self.tdo])
                    mask = concat([v for v in self.mask])
                else:
                    tdi = self.tdi[0]
                    tdo = self.tdo[0]
                    mask = self.mask[0]
                wrvf = p2654model2.rvf.protocols.JTAG_pb2.SDR()
                wrvf.UID = node_uid
                self.nrbits = len(tdi)
                wrvf.nrbits = self.nrbits
                ltdi = self.__vector_to_list(self.nrbits, tdi)
                for v in ltdi:
                    wrvf.tdi.append(v)
                ltdo = self.__vector_to_list(self.nrbits, tdo)
                for v in ltdo:
                    wrvf.tdo.append(v)
                lmask = self.__vector_to_list(self.nrbits, mask)
                for v in lmask:
                    wrvf.mask.append(v)
                pending += 1
                ret = self.__sendRequest(node_uid, wrvf, "SDR")
                if not ret:
                    err += 1
                self.pending = False
                self.capture = False
                self.data_mode = None
            elif self.capture and not self.data_mode:
                # Concatenate vectors together into a single vector to scan
                if len(self.tdi) > 1:
                    tdi = concat([v for v in self.tdi])
                    tdo = concat([v for v in self.tdo])
                    mask = concat([v for v in self.mask])
                else:
                    tdi = self.tdi[0]
                    tdo = self.tdo[0]
                    mask = self.mask[0]
                wrvf = p2654model2.rvf.protocols.JTAG_pb2.SIR()
                wrvf.UID = node_uid
                self.nrbits = len(tdi)
                wrvf.nrbits = self.nrbits
                ltdi = self.__vector_to_list(self.nrbits, tdi)
                for v in ltdi:
                    wrvf.tdi.append(v)
                ltdo = self.__vector_to_list(self.nrbits, tdo)
                for v in ltdo:
                    wrvf.tdo.append(v)
                lmask = self.__vector_to_list(self.nrbits, mask)
                for v in lmask:
                    wrvf.mask.append(v)
                pending += 1
                ret = self.__sendRequest(node_uid, wrvf, "SIR")
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
        self.enddr = message.state
        self.pending = True
        return True

    def __endir_cb(self, node_uid, message):
        self.child_uid = message.UID
        self.endir = message.state
        self.pending = True
        return True

    def __sdr_cb(self, node_uid, message):
        self.child_uid = message.UID
        if not self.cached:
            self.__init_segments()
            self.cached = True
        ndx = 0
        found = False
        for i in self.children_uids:
            if i == message.UID:
                found = True
                break
            ndx += 1
        if found:
            self.tdi[ndx] = intbv(self.ipint2int(message.tdi), min=None, max=None, _nrbits=message.nrbits)
            self.tdo[ndx] = intbv(self.ipint2int(message.tdo), min=None, max=None, _nrbits=message.nrbits)
            self.mask[ndx] = intbv(self.ipint2int(message.mask), min=None, max=None, _nrbits=message.nrbits)
            self.pending = True
            self.capture = True
            self.data_mode = True
            return True
        else:
            return False

    def __sir_cb(self, node_uid, message):
        self.child_uid = message.UID
        if not self.cached:
            self.__init_segments()
            self.cached = True
        ndx = 0
        found = False
        for i in self.children_uids:
            if i == message.UID:
                found = True
                break
            ndx += 1
        if found:
            self.tdi[ndx] = intbv(self.ipint2int(message.tdi), min=None, max=None, _nrbits=message.nrbits)
            self.tdo[ndx] = intbv(self.ipint2int(message.tdo), min=None, max=None, _nrbits=message.nrbits)
            self.mask[ndx] = intbv(self.ipint2int(message.mask), min=None, max=None, _nrbits=message.nrbits)
            self.pending = True
            self.capture = True
            self.data_mode = False
            return True
        else:
            return False

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
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.ENDDR()
            rvf.UID = uid
            rvf.state = message.state
            self.__sendResponse(node_uid, rvf, "ENDDR", uid)
        return True

    def __endir_resp_cb(self, node_uid, message):
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.ENDIR()
            rvf.UID = uid
            rvf.state = message.state
            self.__sendResponse(node_uid, rvf, "ENDIR", uid)
        return True

    def __sdr_resp_cb(self, node_uid, message):
        return self.__data_resp("SDR", node_uid, message)

    def __sir_resp_cb(self, node_uid, message):
        return self.__data_resp("SIR", node_uid, message)

    def __data_resp(self, metaname, node_uid, message):
        tdi = intbv(self.ipint2int(message.tdi), _nrbits=message.nrbits)
        tdo = intbv(self.ipint2int(message.tdo), _nrbits=message.nrbits)
        mask = intbv(self.ipint2int(message.mask), _nrbits=message.nrbits)
        start = 0
        end = 0
        i = 0
        for uid in self.children_uids:
            start = len(self.tdi[i]) + start
            if metaname == "SIR":
                resp = p2654model2.rvf.protocols.JTAG_pb2.SIR()
            else:
                resp = p2654model2.rvf.protocols.JTAG_pb2.SDR()
            resp.UID = uid
            nrbits = len(intbv(self.tdi[i][start:end]))
            ltdi = self.__vector_to_list(self.nrbits, tdi[start:end])
            for v in ltdi:
                resp.tdi.append(v)
            ltdo = self.__vector_to_list(self.nrbits, tdo[start:end])
            for v in ltdo:
                resp.tdo.append(v)
            lmask = self.__vector_to_list(self.nrbits, mask[start:end])
            for v in lmask:
                resp.mask.append(v)
            resp.nrbits = nrbits
            self.__sendResponse(node_uid, resp, metaname, uid)
            end = start
            i += 1
        self.__updateDataValue(node_uid, message.tdo)
        return True

    def __runtest_resp_cb(self, node_uid, message):
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.RUNTEST()
            rvf.UID = uid
            rvf.run_state = message.run_state
            rvf.run_count = message.run_count
            rvf.run_clk = message.run_clk
            rvf.min_time = message.min_time
            rvf.max_time = message.max_time
            rvf.end_state = message.end_state
            self.__sendResponse(node_uid, rvf, "RUNTEST", uid)
        return True

    def __trst_resp_cb(self, node_uid, message):
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
            rvf.UID = uid
            rvf.state = message.state
            self.__sendResponse(node_uid, rvf, "TRST", uid)
        return True

    def __state_resp_cb(self, node_uid, message):
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.STATE()
            rvf.UID = uid
            for s in self.state_message.state:
                rvf.state.append(s)
            rvf.end_state = self.state_message.end_state
            self.__sendResponse(node_uid, rvf, "STATE", uid)
        return True

    def __frequency_resp_cb(self, node_uid, message):
        for uid in self.children_uids:
            rvf = p2654model2.rvf.protocols.JTAG_pb2.TRST()
            rvf.UID = uid
            rvf.cycles = message.cycles
            self.__sendResponse(node_uid, rvf, "FREQUENCY", uid)
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
        self.logger.debug("JTAGChain.__sendRequest({:s}): sending {:s} RVF\n".format(self.name, metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = self.node_uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendRequestCallback(node_uid, wrapper)

    def __sendResponse(self, node_uid, message, metaname, uid):
        self.logger.debug("JTAGChain.__sendResponse({:s}): sending {:s} RVF\n".format(self.name, metaname))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.UID = uid
        wrapper.metaname = metaname
        wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
        wrapper.serialized = message.SerializeToString()
        return self.sendResponseCallback(node_uid, wrapper)

    def __updateDataValue(self, node_uid, tdo):
        self.logger.debug("JTAGChain.__updateDataValue({:s}):\n".format(self.name))
        dvmsg = p2654model2.rvf.rvfmessage_pb2.RVFDataValue()
        dvmsg.UID = node_uid
        for v in tdo:
            dvmsg.data.append(v)
        return self.updateDataValueCallback(node_uid, dvmsg)

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
        self.writeln("Dumping JTAGChain: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("child_uid = {:s}".format(str(self.child_uid)))
        self.writeln("params = {:s}".format(str(self.params)))
        self.writeln("children_uids = {:s}".format(str(self.children_uids)))
        self.writeln("command = {:s}".format(str(self.command)))
        self.dedent()
