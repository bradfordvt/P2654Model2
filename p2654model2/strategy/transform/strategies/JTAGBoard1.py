#!/usr/bin/env python
"""
    Specialized Transformation Strategy for JTAGBoard1 design in the P2654Simulations tester.
    Copyright (C) 2021  Bradford G. Van Treuren

    Specialized Transformation Strategy for JTAGBoard1 design in the P2654Simulations tester.
    This strategy is implemented as a built-in plug-in module wrapped by its own TransformationStrategy
    instance.  To use this strategy, specify the name JTAGBoard1 as the "tstrategy"
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
__date__ = "2021/03/03"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


import logging
from autologging import traced, logged
import p2654model2.rvf.rvfmessage_pb2

# create logger
module_logger = logging.getLogger('p2654model2.strategy.transform.strategies.JTAGBoard1')


@logged
@traced
class JTAGBoard1(object):
    __indent = 0

    def __init__(self):
        self.logger = logging.getLogger('p2654model2.strategy.transform.strategies.JTAGBoard1')
        self.logger.info('Creating an instance of JTAGBoard1')
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
        self.sendObserverCallback = None
        self.registerObserverCallback = None

    def create(self, name, node_uid, children_uids, children_names, params):
        # print("JTAGBoard1 params = {:s}".format(str(params)))
        self.name = name
        self.node_uid = node_uid
        self.children_uids = children_uids
        self.children_names = children_names
        self.params = params
        return None

    def configure(self):
        return True

    def handleRequest(self, node_uid, message):
        self.logger.debug("JTAGBoard1.handleRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return None

    def handleResponse(self, node_uid, message):
        self.logger.debug("JTAGBoard1.handleResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return None

    def getStatus(self, node_uid, timeout):
        print("JTAGBoard1Transform getStatus ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFStatus()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.STATUS
        rvf.message = "OK"
        rvf.code = 0
        return rvf

    def getError(self, node_uid, timeout):
        print("JTAGBoard1Transform getError ({:d}).".format(timeout))
        rvf = p2654model2.rvf.rvfmessage_pb2.RVFError()
        rvf.UID = 0
        rvf.rvf_type = p2654model2.rvf.rvfmessage_pb2.ERROR
        rvf.message = "UNKNOWN"
        rvf.code = 0
        return rvf

    def apply(self, node_uid, timeout=0):
        self.logger.debug("JTAGBoard1.apply({:s}): processing {:d} node_uid\n".format(self.name, node_uid))
        print("JTAGBoard1Transform apply()")
        return 0

    def getCallbackNames(self):
        return []

    def destroy(self, node_uid):
        return None

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

    def indent(self):
        self.__indent += 4

    def dedent(self):
        self.__indent -= 4

    def writeln(self, ln):
        print(" " * self.__indent, ln)

    def dump(self, indent):
        self.__indent = indent
        self.writeln("Dumping JTAGBoard1: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("child_uid = {:s}".format(str(self.child_uid)))
        self.writeln("params = {:s}".format(str(self.params)))
        self.writeln("children_uids = {:s}".format(str(self.children_uids)))
        self.dedent()
