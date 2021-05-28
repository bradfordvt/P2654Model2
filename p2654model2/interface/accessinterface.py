#!/usr/bin/env python
"""
    Primary interface used to send RVF messages between model nodes.
    Copyright (C) 2021  Bradford G. Van Treuren

    Primary interface used to send RVF messages between model nodes.
    The AccessInterface describes the edge relationship between model nodes of the model
    tree describing the UUT hierarchical structure.

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


from threading import Event

import logging
from autologging import traced, logged


import p2654model2.rvf.rvfmessage_pb2
# create logger
module_logger = logging.getLogger('P2654Model2.interface.accessinterface')


@logged
@traced
class AccessInterface(object):
    __indent = 0
    stop_event = Event()

    @staticmethod
    def stop():
        AccessInterface.stop_event.set()

    def __init__(self):
        self.logger = logging.getLogger('P2654Model2.interface.accessinterface')
        self.logger.info('Creating an instance of AccessInterface')
        self.req_cb = None
        self.resp_cb = {}
        self.updreq_cb = {}
        self.updresp_cb = {}
        self.current_uid = None

    def sendRequest(self, rvf):
        self.logger.debug("AccessInterface: Request(uid={:d}, command={:s})\n".format(rvf.UID, rvf.metaname))
        if self.req_cb is not None:
            self.logger.debug("AccessInterface.sendRequest(): Before call to self.req_cb().\n")
            self.current_uid = rvf.UID
            self.logger.debug("AccessInterface: Dispatching Request(uid={:d}, command={:s})\n".format(rvf.UID,
                                                                                                      rvf.metaname))
            self.logger.debug("dump of req_cb\n{:s}\n".format(str(self.req_cb)))
            return self.req_cb(rvf)
        else:
            return None

    def set_req_callback(self, uid, cb):
        self.logger.debug("set_req_callback({:d}, {:s})\n".format(uid, str(cb)))
        self.req_cb = cb

    def sendResponse(self, rvf):
        self.logger.debug("AccessInterface: Response(uid={:d}, command={:s})\n".format(rvf.UID, rvf.metaname))
        if self.resp_cb is not None:
            self.logger.debug("AccessInterface: Dispatching Response(uid={:d}, command={:s})\n".format(rvf.UID,
                                                                                                       rvf.metaname))
            return self.resp_cb[self.current_uid](rvf)
        else:
            return None

    def set_resp_callback(self, uid, cb):
        self.resp_cb.update({uid: cb})

    def updateRequest(self, rvf):
        self.logger.debug("AccessInterface: updateRequest(uid={:d}, command={:s})\n".format(rvf.UID, rvf.metaname))
        if self.updreq_cb is not None:
            self.logger.debug("AccessInterface: Dispatching updateRequest(uid={:d}, command={:s})\n".format(rvf.UID,
                                                                                                            rvf.metaname))
            self.logger.debug("dump of updreq_cb\n{:s}\n".format(str(self.updreq_cb)))
            return self.updreq_cb[rvf.UID](rvf)
        else:
            return None

    def set_update_req_callback(self, uid, cb):
        self.logger.debug("set_upd_req_callback({:d}, {:s})\n".format(uid, str(cb)))
        self.updreq_cb = cb

    def updateResponse(self, rvf):
        self.logger.debug(
            "AccessInterface: updateResponse(uid={:d}, command={:s})\n".format(rvf.UID, rvf.metaname))
        if self.updresp_cb is not None:
            self.logger.debug("AccessInterface: Dispatching updateResponse(uid={:d}, command={:s})\n".format(rvf.UID,
                                                                                                             rvf.metaname))
            return self.updresp_cb[self.current_uid](rvf)
        else:
            return None

    def set_update_resp_callback(self, uid, cb):
        self.updresp_cb.update({uid: cb})

    def indent(self):
        AccessInterface.__indent += 4

    def dedent(self):
        AccessInterface.__indent -= 4

    def writeln(self, ln):
        print(" " * AccessInterface.__indent, ln)

    def dump(self, indent):
        AccessInterface.__indent = indent
        self.writeln("Dumping AccessInterface:")
        self.indent()
        self.writeln("req_cb = {:s}".format(str(self.req_cb)))
        self.writeln("resp_cb = {:s}".format(str(self.resp_cb)))
        self.writeln("updreq_cb = {:s}".format(str(self.updreq_cb)))
        self.writeln("updresp_cb = {:s}".format(str(self.updresp_cb)))
        self.writeln("current_uid = {:s}".format(str(self.current_uid)))
        self.dedent()
