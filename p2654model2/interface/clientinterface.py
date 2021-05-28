#!/usr/bin/env python
"""
    Interface class defining the API gateway to an upper level node.
    Copyright (C) 2021  Bradford G. Van Treuren

    Interface class defining the API gateway to an upper level node.
    The ClientInterface class interfaces with the corresponding HostInterface class
    via a commonly defined AccessInterface object.  The ClientInterface class defines the
    handlers for response messages sent by the HostInterface back to the ClientInterface.
    There may be multiple Clients and therefore multiple ClientInterfaces mating to a single
    HostInterface instance.

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


module_logger = logging.getLogger('P2654Model2.interface.clientinterface')


@logged
@traced
class ClientInterface(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('P2654Model2.interface.clientinterface')
        self.logger.info('Creating an instance of ClientInterface')
        self.access_interface = None
        self.transform_engine = None

    def handleResponse(self, message):
        self.logger.debug("ClientInterface.handleResponse({:s}): processing {:s} RVF\n".format(self.transform_engine.name, message.metaname))
        # ret = self.transform_engine.handleModelResponse(message)
        ret = self.transform_engine.handleResponse(message)
        return ret

    def handleUpdateRequest(self, message):
        self.logger.debug("ClientInterface.handleUpdateRequest({:s}): processing {:s} RVF\n".format(self.transform_engine.name, message.metaname))
        ret = self.transform_engine.handleUpdateRequest(message)
        return ret

    def handleUpdateResponse(self, message):
        self.logger.debug("ClientInterface.handleUpdateResponse({:s}): processing {:s} RVF\n".format(self.transform_engine.name, message.metaname))
        ret = self.transform_engine.handleUpdateResponse(message)
        return ret

    # def updateRequest(self, message):
    #     self.logger.debug("ClientInterface.updateRequest({:s}): processing {:s} RVF\n".format(self.transform_engine.name, message.metaname))
    #     ret = self.access_interface.updateRequest(message)
    #     return ret
    #
    # def updateResponse(self, message):
    #     self.logger.debug("ClientInterface.updateResponse({:s}): processing {:s} RVF\n".format(self.transform_engine.name, message.metaname))
    #     ret = self.access_interface.updateResponse(message)
    #     return ret

    def sendRequest(self, message):
        self.logger.debug("ClientInterface.sendRequest({:s}): processing {:s} RVF\n".format(self.transform_engine.name, message.metaname))
        ret = self.access_interface.sendRequest(message)
        return ret

    def registerAccessInterface(self, access_interface):
        self.access_interface = access_interface

    def registerTransformEngine(self, transform_engine):
        self.transform_engine = transform_engine

    def set_resp_callback(self, uid, cb):
        self.access_interface.set_resp_callback(uid, cb)

    def set_update_req_callback(self, uid, cb):
        self.access_interface.set_update_req_callback(uid, cb)

    def set_update_resp_callback(self, uid, cb):
        self.access_interface.set_update_resp_callback(uid, cb)

    def indent(self):
        ClientInterface.__indent += 4

    def dedent(self):
        ClientInterface.__indent -= 4

    def writeln(self, ln):
        print(" " * ClientInterface.__indent, ln)

    def dump(self, indent):
        ClientInterface.__indent = indent
        self.writeln("Dumping ClientInterface:")
        self.indent()
        self.access_interface.dump(ClientInterface.__indent)
        self.dedent()
