#!/usr/bin/env python
"""
    Generalized injector for GPIO type node registers.
    Copyright (C) 2021  Bradford G. Van Treuren

    Generalized injector for GPIO type node registers.
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
__date__ = "2021/03/10"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


import p2654model2.rvf.rvfmessage_pb2
import p2654model2.rvf.commands.register_pb2
import p2654model2.rvf.protocols.GPIO_pb2

import logging
from autologging import traced, logged


module_logger = logging.getLogger('p2654model2.injectors.GPio')


@logged
@traced
class GPio(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('p2654model2.injectors.GPio')
        self.logger.info('Creating an instance of GPio')
        self.name = None
        self.node_uid = None
        self.iid = None
        self.injector = None
        self.parameters = None
        self.cproto = None
        self.size = 0
        self.safe = None
        self.input = []
        self.output = []
        self.has_write = False
        self.has_read = False
        self.sendRequestCallback = None
        self.updateDataValueCallback = None

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
                self.safe = sint
        else:
            self.safe = 0
        return None

    def apply(self, iid, timeout):
        pending = 0
        err = 0
        if self.has_write:
            self.logger.debug("GPio.apply(): processing OUTPUT RVF\n")
            metaname = "OUTPUT"
            rvf1 = p2654model2.rvf.protocols.GPIO_pb2.OUTPUT()
            rvf1.UID = self.node_uid
            rvf1.value = self.output[0]
            self.has_write = False
            pending += 1
            if not self.__sendRequest(self.node_uid, rvf1, metaname):
                err += 1
        elif self.has_read:
            self.logger.debug("GPio.apply(): processing INPUT RVF\n")
            metaname = "INPUT"
            rvf1 = p2654model2.rvf.protocols.GPIO_pb2.INPUT()
            rvf1.UID = self.node_uid
            if len(self.input):
                rvf1.value = self.input[0]
            self.has_read = False
            pending += 1
            if not self.__sendRequest(self.node_uid, rvf1, metaname):
                err += 1
        else:
            self.logger.debug("GPio.apply(): processing no RVF\n")
            return 0
        if err:
            return -1
        elif pending:
            return 1
        else:
            return 0

    def destroy(self, iid):
        return None

    def get_commands(self, iid):
        return ["WRITE", "READ", "GET"]

    def handleResponse(self, iid, message):
        self.logger.debug("GPio.handleResponse(): handling {:s} RVF.\n".format(message.metaname))
        # message = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        # message.ParseFromString(rvf_message)
        if message.metaname == "INPUT":
            s = p2654model2.rvf.protocols.GPIO_pb2.INPUT()
            s.ParseFromString(message.serialized)
            return self.__input_resp_cb(iid, s)
        elif message.metaname == "OUTPUT":
            s = p2654model2.rvf.protocols.GPIO_pb2.OUTPUT()
            s.ParseFromString(message.serialized)
            return self.__output_resp_cb(iid, s)

    def handleCommand(self, iid, wrapper):
        self.logger.debug("GPio.handleCommand(): handling command ({:s}).\n".format(wrapper.metaname))
        print("gpio handling command ({:s}).".format(wrapper.metaname))
        if wrapper.metaname == "WRITE":
            s = p2654model2.rvf.commands.register_pb2.WRITE()
            s.ParseFromString(wrapper.serialized)
            return self.__output_cb(iid, s)
        elif wrapper.metaname == "READ":
            s = p2654model2.rvf.commands.register_pb2.READ()
            s.ParseFromString(wrapper.serialized)
            return self.__input_cb(iid, s)
        elif wrapper.metaname == "GET":
            s = p2654model2.rvf.commands.register_pb2.GET()
            s.ParseFromString(wrapper.serialized)
            return self.__get_cb(iid, s)
        return None

    def set_sendRequestCallback(self, callback):
        self.sendRequestCallback = callback

    def set_updateDataValueCallback(self, callback):
        self.updateDataValueCallback = callback

    def __output_cb(self, iid, msg):
        if msg.nrbits > 32:
            raise AssertionError("Wrong number of bits.")
        self.output = msg.value
        self.has_write = True
        return True

    def __input_cb(self, iid, msg):
        if msg.nrbits > 32:
            raise AssertionError("Wrong number of bits.")
        self.input = msg.value
        self.has_read = True
        return True

    def __get_cb(self, iid, msg):
        if msg.nrbits > 32:
            raise AssertionError("Wrong number of bits.")
        return True

    def __input_resp_cb(self, iid, msg):
        if iid != self.iid:
            raise AssertionError("Route of message to wrong iid.")
        self.input = msg.value
        self.__updateDataValue(iid)
        self.has_read = False
        return True

    def __output_resp_cb(self, iid, msg):
        if iid != self.iid:
            raise AssertionError("Route of message to wrong iid.")
        self.output = msg.value
        self.has_write = False
        return True

    def __sendRequest(self, uid, message, metaname):
        self.logger.debug("GPio.__sendRequest(): sending {:s} RVF.\n".format(metaname))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        rvf.UID = uid
        rvf.metaname = metaname
        rvf.serialized = message.SerializeToString()
        return self.sendRequestCallback(rvf)

    def __updateDataValue(self, node_uid):
        self.logger.debug("GPio.__updateDataValue({:s}):\n".format(self.name))
        dvmsg = p2654model2.rvf.rvfmessage_pb2.RVFDataValue()
        dvmsg.UID = node_uid
        dvmsg.data.append(self.input)
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

    def indent(self):
        self.__indent += 4

    def dedent(self):
        self.__indent -= 4

    def writeln(self, ln):
        print("" * self.__indent, ln)

    def dump(self, indent):
        self.__indent = indent
        self.writeln("Dumping GPio: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("iid = {:d}".format(self.iid))
        self.writeln("parameters = {:s}".format(self.parameters))
        self.writeln("injector = {:s}".format(self.injector))
        self.writeln("size = {:d}".format(self.size))
        self.writeln("safe = {:s}".format(self.safe))
        self.writeln("cproto = {:s}".format(self.cproto))
        self.dedent()
