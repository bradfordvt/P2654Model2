#!/usr/bin/env python
"""
    Debug strategy built-in example for unit test case.
    Copyright (C) 2021  Bradford G. Van Treuren

    Debug strategy built-in example for unit test case.

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
__date__ = "2021/02/06"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


import p2654model2.rvf.protocols.JTAG_pb2
import p2654model2.rvf.protocols.dummytest_pb2
import p2654model2.rvf.rvfmessage_pb2


class dummydstrategy(object):
    def __init__(self):
        self.log = None
        self.name = None
        self.node_uid = None
        self.command = None
        self.children_uids = None
        self.params = None
        self.reqQ = []
        self.respQ = []
        self.updateReqQ = []
        self.updateRespQ = []
        
    def create(self, name, node_uid, children_uids, params):
        logfd = open("dummydstrategy.log", "w")
        print("dummydstrategy params = {:s}".format(params))
        self.log = logfd
        self.name = name
        self.node_uid = node_uid
        self.children_uids = children_uids
        self.params = params
        self.log.write("create()\n=========================\n")
        self.log.write("name = {:s}\n".format(name))
        self.log.write("node_uid = {:d}\n".format(node_uid))
        self.log.write("children_uids = {:s}\n".format(str(children_uids)))
        self.log.write("params = {:s}\n".format(params))
        self.log.write("++++++++++++++++++++++++++++++++++++++++++++++\n")
        return None

    def handleRequest(self, node_uid, msg):
        self.log.write("handleRequest()\n=========================\n")
        self.log.write("node_uid = {:d}\n".format(node_uid))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.ParseFromString(msg)
        m = p2654model2.rvf.protocols.JTAG_pb2.SDR()
        m.ParseFromString(wrapper.serialized)
        self.log.write("msg = {:s}\n".format(str(m)))
        self.log.write("++++++++++++++++++++++++++++++++++++++++++++++\n")
        return None

    def handleResponse(self, node_uid, msg):
        self.log.write("handleResponse()\n=========================\n")
        self.log.write("node_uid = {:d}\n".format(node_uid))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.ParseFromString(msg)
        m = p2654model2.rvf.protocols.JTAG_pb2.SDR()
        m.ParseFromString(wrapper.serialized)
        self.log.write("msg = {:s}\n".format(str(m)))
        self.log.write("++++++++++++++++++++++++++++++++++++++++++++++\n")
        return None

    def updateRequest(self, node_uid, msg):
        self.log.write("updateRequest()\n=========================\n")
        self.log.write("node_uid = {:d}\n".format(node_uid))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.ParseFromString(msg)
        m = p2654model2.rvf.protocols.JTAG_pb2.SDR()
        m.ParseFromString(wrapper.serialized)
        self.log.write("msg = {:s}\n".format(str(m)))
        self.log.write("++++++++++++++++++++++++++++++++++++++++++++++\n")
        return None

    def updateResponse(self, node_uid, msg):
        self.log.write("updateResponse()\n=========================\n")
        self.log.write("node_uid = {:d}\n".format(node_uid))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.ParseFromString(msg)
        m = p2654model2.rvf.protocols.JTAG_pb2.SDR()
        m.ParseFromString(wrapper.serialized)
        self.log.write("msg = {:s}\n".format(str(m)))
        self.log.write("++++++++++++++++++++++++++++++++++++++++++++++\n")
        return None

    def sendRequest(self, node_uid, msg):
        self.log.write("sendRequest()\n=========================\n")
        self.log.write("node_uid = {:d}\n".format(node_uid))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.ParseFromString(msg)
        m = p2654model2.rvf.protocols.JTAG_pb2.SDR()
        m.ParseFromString(wrapper.serialized)
        self.log.write("msg = {:s}\n".format(str(m)))
        self.log.write("++++++++++++++++++++++++++++++++++++++++++++++\n")
        return None

    def sendResponse(self, node_uid, msg):
        self.log.write("sendResponse()\n=========================\n")
        self.log.write("node_uid = {:d}\n".format(node_uid))
        wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
        wrapper.ParseFromString(msg)
        m = p2654model2.rvf.protocols.JTAG_pb2.SDR()
        m.ParseFromString(wrapper.serialized)
        self.log.write("msg = {:s}\n".format(str(m)))
        self.log.write("++++++++++++++++++++++++++++++++++++++++++++++\n")
        return None

    def getStatus(self, node_uid, timeout):
        self.log.write("getStatus()\n=========================\n")
        self.log.write("node_uid = {:d}\n".format(node_uid))
        self.log.write("timeout = {:d}\n".format(timeout))
        self.log.write("++++++++++++++++++++++++++++++++++++++++++++++\n")
        return None

    def getError(self, node_uid, timeout):
        self.log.write("getError()\n=========================\n")
        self.log.write("node_uid = {:d}\n".format(node_uid))
        self.log.write("timeout = {:d}\n".format(timeout))
        self.log.write("++++++++++++++++++++++++++++++++++++++++++++++\n")
        return None

    def apply(self, node_uid, timeout=0):
        self.log.write("apply()\n=========================\n")
        self.log.write("node_uid = {:d}\n".format(node_uid))
        self.log.write("timeout = {:d}\n".format(timeout))
        self.log.write("++++++++++++++++++++++++++++++++++++++++++++++\n")
        return 0

    def getCallbackNames(self):
        return ["SDR", "RUNTEST", "RESET"]

    def destroy(self, node_uid):
        self.log.write("destroy()\n=========================\n")
        self.log.write("node_uid = {:d}\n".format(node_uid))
        self.log.write("++++++++++++++++++++++++++++++++++++++++++++++\n")
        self.log.close()
        return None
