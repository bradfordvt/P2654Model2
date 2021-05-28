#!/usr/bin/env python
"""
    The TestInjectionInterface class is used to send messages between an injector and corresponding
    injection strategy.
    Copyright (C) 2021  Bradford G. Van Treuren

    The TestInjectionInterface class is used to send messages between an injector and corresponding
    injection strategy.

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


module_logger = logging.getLogger('P2654Model2.interface.testinjectioninterface')


@logged
@traced
class TestInjectionInterface(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('P2654Model2.interface.testinjectioninterface')
        self.logger.info('Creating an instance of TestInjectionInterface')
        self.access_interface = None
        self.__transform_engine = None

    def handleRequest(self, message):
        self.logger.debug("TestInjectionInterface.handleRequest({:s}): processing {:s} RVF\n".format(self.__transform_engine.name, message.metaname))
        ret = self.__transform_engine.handleInjectionRequest(message)
        return ret

    def sendRequest(self, message):
        self.logger.debug("TestInjectionInterface.sendRequest({:s}): processing {:s} RVF\n".format(self.__transform_engine.name, message.metaname))
        ret = self.access_interface.sendRequest(message)
        return ret

    def sendResponse(self, message):
        self.logger.debug("TestInjectionInterface.sendResponse({:s}): processing {:s} RVF\n".format(self.__transform_engine.name, message.metaname))
        ret = self.access_interface.sendResponse(message)
        return ret

    def handleCommand(self, message):
        self.logger.debug("TestInjectionInterface.handleCommand({:s}): processing {:s} RVF\n".format(self.__transform_engine.name, message.metaname))
        return self.__injector.handleCommand(message)

    def updateDataValue(self, message):
        self.logger.debug("TestInjectionInterface.updateDataValue({:s}): processing {:s} RVF\n".format(self.__transform_engine.name, message.metaname))
        return self.__transform_engine.updateDataValue(message)

    def registerAccessInterface(self, uid, __access_interface):
        self.access_interface = __access_interface
        self.access_interface.set_req_callback(uid, self.handleRequest)

    def registerTransformEngine(self, __transform_engine):
        self.__transform_engine = __transform_engine

    def registerInjector(self, iid, injector):
        self.__injector = injector
        self.access_interface.set_update_req_callback(iid, self.__injector.updateRequest)
        self.access_interface.set_resp_callback(iid, self.__injector.handleResponse)

    def indent(self):
        TestInjectionInterface.__indent += 4

    def dedent(self):
        TestInjectionInterface.__indent -= 4

    def writeln(self, ln):
        print(" " * TestInjectionInterface.__indent, ln)

    def dump(self, indent):
        TestInjectionInterface.__indent = indent
        self.writeln("Dumping TestInjectionInterface:")
        self.indent()
        if self.access_interface:
            self.access_interface.dump(TestInjectionInterface.__indent)
        else:
            self.writeln("AccessInterface is undefined")
        self.dedent()
