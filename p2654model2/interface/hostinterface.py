#!/usr/bin/env python
"""
    Interface class defining the API gateway to an lower level nodes.
    Copyright (C) 2021  Bradford G. Van Treuren

    Interface class defining the API gateway to an lower level nodes.
    The HostInterface class interfaces with the corresponding ClientInterface classes
    via a commonly defined AccessInterface object.  The HostInterface class defines the
    handlers for request messages sent by the ClientInterface to the HostInterface.
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
__date__ = "2021/03/03"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


import logging
from autologging import traced, logged


module_logger = logging.getLogger('P2654Model2.interface.hostinterface')


@logged
@traced
class HostInterface(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('P2654Model2.interface.hostinterface')
        self.logger.info('Creating an instance of HostInterface')
        self.access_interface = None
        self.transform_engine = None

    def handleRequest(self, message):
        self.logger.debug("HostInterface.handleRequest({:s}): processing {:s} RVF\n".format(self.transform_engine.name, message.metaname))
        ret = self.transform_engine.handleModelRequest(message)
        return ret

    def sendResponse(self, message):
        self.logger.debug("HostInterface.sendResponse({:s}): processing {:s} RVF\n".format(self.transform_engine.name, message.metaname))
        ret = self.access_interface.sendResponse(message)
        return ret

    def updateRequest(self, message):
        self.logger.debug("HostInterface.updateRequest({:s}): processing {:s} RVF\n".format(self.transform_engine.name, message.metaname))
        ret = self.access_interface.updateRequest(message)
        return ret

    def updateResponse(self, message):
        self.logger.debug("HostInterface.updateResponse({:s}): processing {:s} RVF\n".format(self.transform_engine.name, message.metaname))
        ret = self.access_interface.updateResponse(message)
        return ret

    def registerAccessInterface(self, access_interface):
        self.access_interface = access_interface

    def registerTransformEngine(self, transform_engine):
        self.transform_engine = transform_engine

    def set_req_callback(self, uid, cb):
        self.access_interface.set_req_callback(uid, cb)

    def indent(self):
        HostInterface.__indent += 4

    def dedent(self):
        HostInterface.__indent -= 4

    def writeln(self, ln):
        print(" " * HostInterface.__indent, ln)

    def dump(self, indent):
        HostInterface.__indent = indent
        self.writeln("Dumping HostInterface:")
        self.indent()
        self.access_interface.dump(HostInterface.__indent)
        self.dedent()
