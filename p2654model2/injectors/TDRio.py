#!/usr/bin/env python
"""
    Generalized injector for JTAG TDR type node registers.
    Copyright (C) 2021  Bradford G. Van Treuren

    Generalized injector for JTAG TDR type node registers.
    An injector handles commands sent from the application code to inject stimulus into the model
    at the hierarchical level in the tree where the node resides.

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


from myhdl import intbv
from threading import Lock, Condition
import p2654model2.rvf.rvfmessage_pb2
import p2654model2.rvf.commands.register_pb2
import p2654model2.rvf.protocols.SCAN_pb2


import logging
from autologging import traced, logged

module_logger = logging.getLogger('P2654Model2.injectors.TDRio')


@logged
@traced
class TDRio(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('P2654Model2.injectors.TDRio')
        self.logger.info('Creating an instance of TDRio')
        self.name = None
        self.node_uid = None
        self.iid = None
        self.injector = None
        self.parameters = None
        self.cproto = None
        self.data = None
        self.si = []
        self.so = []
        self.size = None
        self.safe = []
        self.has_write = False
        self.has_read = False
        self.endstate = p2654model2.rvf.commands.register_pb2.NOP1_STABLE
        self.sendRequestCallback = None
        self.updateDataValueCallback = None
        # mutex to regulate the access to the response_received_cv variable
        self.response_mutex = Lock()
        # condition variable: notifies the host callback that the
        # thread related to a client response has finished the request
        self.response_cv = Condition(self.response_mutex)
        # variable coupled to response_cv to avoid spurious wakeups
        self.response_v = 0
        self.response = None

        self.local_access_mutex = Lock()

    def create(self, name, node_uid, iid, injector, parameters, cproto):
        self.name = name
        self.node_uid = node_uid
        self.iid = iid
        self.injector = injector
        self.parameters = parameters
        self.cproto = cproto
        data = self.__parse_params(self.parameters)
        if len(data['kwargs']):
            size = data['kwargs'].get('size')
            if size is None:
                raise SyntaxError("TDR size not specified for {:s} with injector.".format(name))
            else:
                self.size = int(size)
        else:
            self.size = 0
        if len(data['kwargs']):
            safe = data['kwargs'].get('safe')
            if safe is None:
                raise SyntaxError("TDR safe value not specified for {:s} with injector.".format(name))
            else:
                if len(safe) > 1 and safe[0] == '0' and safe[1] == 'x':
                    sint = int(safe, 16)
                elif len(safe) > 1 and safe[0] == '0' and safe[1] == 'b':
                    sint = int(safe, 2)
                else:
                    sint = int(safe)
                self.safe = self.__vector_to_list(self.size, sint)
                self.si = self.safe
                self.so = self.safe
        else:
            self.safe = self.__vector_to_list(self.size, intbv(0))
            self.si = self.safe
            self.so = self.safe
        return None

    def get_value(self):
        return self.so

    def apply(self, iid, timeout):
        metaname = ""
        pending = 0
        err = 0
        rvf1 = None
        if self.has_write and self.has_read:
            self.logger.debug("TDRio.apply(): processing CSU RVF\n")
            metaname = "CSU"
            rvf1 = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            self.local_access_mutex.acquire()
            for v in self.so:
                rvf1.so_vector.append(v)
            for v in self.si:
                rvf1.si_vector.append(v)
            self.local_access_mutex.release()
            pending += 1
            self.has_write = False
            self.has_read = False
        elif self.has_write:
            self.logger.debug("TDRio.apply(): processing SU RVF\n")
            metaname = "SU"
            rvf1 = p2654model2.rvf.protocols.SCAN_pb2.SU()
            self.local_access_mutex.acquire()
            for v in self.si:
                rvf1.si_vector.append(v)
            self.local_access_mutex.release()
            pending += 1
            self.has_write = False
        elif self.has_read:
            self.logger.debug("TDRio.apply(): processing CS RVF\n")
            metaname = "CS"
            rvf1 = p2654model2.rvf.protocols.SCAN_pb2.CS()
            self.local_access_mutex.acquire()
            for v in self.so:
                rvf1.so_vector.append(v)
            self.local_access_mutex.release()
            pending += 1
            self.has_read = False
        else:
            self.logger.debug("TDRio.apply(): processing no RVF\n")
            return 0
        rvf1.UID = self.node_uid
        rvf1.nrbits = self.size
        if not self.__sendRequest(self.node_uid, rvf1, metaname):
            err += 1
        if err:
            return -1
        elif pending:
            return 1
        else:
            return 0

    def destroy(self, iid):
        return None

    def get_commands(self, iid):
        return ["WRITE", "READ", "GET", "SHIFT", "ENDSTATE"]

    def handleResponse(self, iid, message):
        self.logger.debug("GPio.handleResponse(): handling {:s} RVF.\n".format(message.metaname))
        # message = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        # message.ParseFromString(rvf_message)
        if message.metaname == "CSU":
            s = p2654model2.rvf.protocols.SCAN_pb2.CSU()
            s.ParseFromString(message.serialized)
            return self.__csu_resp_cb(iid, s)
        elif message.metaname == "SU":
            s = p2654model2.rvf.protocols.SCAN_pb2.SU()
            s.ParseFromString(message.serialized)
            return self.__su_resp_cb(iid, s)
        elif message.metaname == "CS":
            s = p2654model2.rvf.protocols.SCAN_pb2.CS()
            s.ParseFromString(message.serialized)
            return self.__cs_resp_cb(iid, s)
        elif message.metaname == "S":
            s = p2654model2.rvf.protocols.SCAN_pb2.S()
            s.ParseFromString(message.serialized)
            return self.__s_resp_cb(iid, s)
        elif message.metaname == "ENDSTATE":
            s = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
            s.ParseFromString(message.serialized)
            return self.__endstate_resp_cb(iid, s)

    def handleCommand(self, iid, wrapper):
        self.logger.debug("TDRio.handleCommand(): handling command ({:s}).\n".format(wrapper.metaname))
        print("tdrio handling command ({:s}).".format(wrapper.metaname))
        if wrapper.metaname == "WRITE":
            s = p2654model2.rvf.commands.register_pb2.WRITE()
            s.ParseFromString(wrapper.serialized)
            return self.__write_cb(iid, s)
        elif wrapper.metaname == "READ":
            s = p2654model2.rvf.commands.register_pb2.READ()
            s.ParseFromString(wrapper.serialized)
            return self.__read_cb(iid, s)
        elif wrapper.metaname == "GET":
            s = p2654model2.rvf.commands.register_pb2.GET()
            s.ParseFromString(wrapper.serialized)
            return self.__get_cb(iid, s)
        elif wrapper.metaname == "SHIFT":
            s = p2654model2.rvf.commands.register_pb2.SHIFT()
            s.ParseFromString(wrapper.serialized)
            return self.__shift_cb(iid, s)
        elif wrapper.metaname == "ENDSTATE":
            s = p2654model2.rvf.commands.register_pb2.SHIFT()
            s.ParseFromString(wrapper.serialized)
            return self.__endstate_cb(iid, s)
        return None

    def set_sendRequestCallback(self, callback):
        self.sendRequestCallback = callback

    def set_updateDataValueCallback(self, callback):
        self.updateDataValueCallback = callback

    def __write_cb(self, iid, msg):
        if msg.nrbits != self.size:
            raise ValueError("Wrong number of bits")
        self.local_access_mutex.acquire()
        self.si = []
        for v in msg.value:
            self.si.append(v)
        self.has_write = True
        self.local_access_mutex.release()
        return True

    def __read_cb(self, iid, msg):
        if msg.nrbits != self.size:
            raise ValueError("Wrong number of bits")
        self.local_access_mutex.acquire()
        self.so = []
        for v in msg.value:
            self.so.append(v)
        self.has_read = True
        self.local_access_mutex.release()
        return True

    def __get_cb(self, iid, msg):
        return True

    def __shift_cb(self, iid, msg):
        ret = True
        metaname = "S"
        rvf1 = p2654model2.rvf.protocols.SCAN_pb2.S()
        rvf1.UID = iid
        rvf1.nrbits = msg.nrbits
        for v in msg.si_vector:
            rvf1.si_vector.append(v)
        for v in msg.so_vector:
            rvf1.so_vector.append(v)
        if not self.__sendRequest(iid, rvf1, metaname):
            ret = False
        return ret

    def __endstate_cb(self, iid, msg):
        ret = True
        metaname = "ENDSTATE"
        rvf1 = p2654model2.rvf.protocols.SCAN_pb2.ENDSTATE()
        rvf1.UID = iid
        if msg.state == p2654model2.rvf.commands.register_pb2.NOP1_STABLE:
            rvf1.state = p2654model2.rvf.protocols.SCAN_pb2.NOP1_STABLE
        elif msg.state == p2654model2.rvf.commands.register_pb2.NOP2_STABLE:
            rvf1.state = p2654model2.rvf.protocols.SCAN_pb2.NOP2_STABLE
        elif msg.state == p2654model2.rvf.commands.register_pb2.NOP4_STABLE:
            rvf1.state = p2654model2.rvf.protocols.SCAN_pb2.NOP4_STABLE
        else:
            raise AssertionError("Invalid ENDSTATE detected.")
        if not self.__sendRequest(iid, rvf1, metaname):
            ret = False
        return ret

    def __csu_resp_cb(self, iid, msg):
        if iid != self.iid:
            raise AssertionError("Route of message to wrong iid.")
        self.local_access_mutex.acquire()
        self.so = []
        self.si = []
        for v in msg.so_vector:
            self.so.append(v)
        for v in msg.si_vector:
            self.si.append(v)
        self.__updateDataValue(iid)
        self.has_read = False
        self.has_write = False
        self.local_access_mutex.release()
        return True

    def __su_resp_cb(self, iid, msg):
        if iid != self.iid:
            raise AssertionError("Route of message to wrong iid.")
        self.local_access_mutex.acquire()
        self.so = []
        for v in msg.so_vector:
            self.so.append(v)
        self.has_write = False
        self.has_read = False
        self.__updateDataValue(iid)
        self.local_access_mutex.release()
        return True

    def __cs_resp_cb(self, iid, msg):
        if iid != self.iid:
            raise AssertionError("Route of message to wrong iid.")
        self.local_access_mutex.acquire()
        self.si = []
        for v in msg.si_vector:
            self.si.append(v)
        self.has_write = False
        self.has_read = False
        self.local_access_mutex.release()
        return True

    def __s_resp_cb(self, iid, msg):
        if iid != self.iid:
            raise AssertionError("Route of message to wrong iid.")
        self.local_access_mutex.acquire()
        self.so = []
        self.si = []
        for v in msg.so_vector:
            self.so.append(v)
        for v in msg.si_vector:
            self.si.append(v)
        self.has_write = False
        self.has_read = False
        self.__updateDataValue(iid)
        self.local_access_mutex.release()
        return True

    def __endstate_resp_cb(self, iid, msg):
        if iid != self.iid:
            raise AssertionError("Route of message to wrong iid.")
        return True

    def __sendRequest(self, uid, message, metaname):
        self.logger.debug("TDRio.__sendRequest(): sending {:s} RVF.\n".format(metaname))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        rvf.UID = uid
        rvf.metaname = metaname
        rvf.serialized = message.SerializeToString()
        return self.sendRequestCallback(rvf)

    def __updateDataValue(self, node_uid):
        self.logger.debug("TDRio.__updateDataValue({:s}):\n".format(self.name))
        dvmsg = p2654model2.rvf.rvfmessage_pb2.RVFDataValue()
        dvmsg.UID = node_uid
        for v in self.so:
            dvmsg.data.append(v)
        return self.updateDataValueCallback(node_uid, dvmsg)

    def __parse_params(self, s):
        data = {"kwargs": {}, "args": []}
        params = s.split(" ")
        for item in params:
            if "=" in item:
                k = item.split("=")
                data['kwargs'][k[0]] = k[1]
            else:
                data['args'].append(item)
        return data

    def __vector_to_list(self, size, value):
        bvlist = []
        bv = intbv(value)
        words = (size + 31) // 32
        while words:
            bvlist.append(bv & 0xFFFFFFFF)
            bv = bv >> 32
            words -= 1
        return bvlist

    def indent(self):
        self.__indent += 4

    def dedent(self):
        self.__indent -= 4

    def writeln(self, ln):
        print("" * self.__indent, ln)

    def dump(self, indent):
        self.__indent = indent
        self.writeln("Dumping TDRio: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("iid = {:d}".format(self.iid))
        self.writeln("parameters = {:s}".format(self.parameters))
        self.writeln("injector = {:s}".format(self.injector))
        self.writeln("size = {:d}".format(self.size))
        self.writeln("safe = {:s}".format(self.safe))
        self.writeln("cproto = {:s}".format(self.cproto))
        self.dedent()
