#!/usr/bin/env python
"""
    Wrapper class for accessing debug strategies plugin modules.
    Copyright (C) 2021  Bradford G. Van Treuren

    Wrapper class for accessing debug strategies plugin modules.

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


from p2654model2.builder.moduleloader import ModuleLoader

import logging
from autologging import traced, logged

module_logger = logging.getLogger('P2654Model2.strategy.transforms.strategies.TAPTransform')


@logged
@traced
class DebugStrategy(object):
    __indent = 0

    def __init__(self, name):
        self.logger = logging.getLogger('P2654Model2.strategy.debug.debugstrategy')
        self.logger.info('Creating an instance of DebugStrategy({:s})'.format(name))
        self.name = name
        self.child_uids = None
        self.node_uid = None
        self.dstrategy = None
        self.module = None
        self.parameters = None
        self.class_obj = None

    def create(self, params):
        self.parameters = params
        ml = ModuleLoader.get_moduleloader()
        self.module = ml.load(self.dstrategy, self.dstrategy)
        if self.module is None:
            self.module = ml.load("debugwrap", self.dstrategy)
        if self.module is None:
            raise AssertionError("Class {:s} could not be found in any modules.".format(self.dstrategy))
        cls = getattr(self.module, self.dstrategy)
        self.class_obj = cls()
        return self.class_obj.create(self.name, self.node_uid, self.child_uids, params)

    def handleRequest(self, message):
        self.logger.debug("DebugStrategy.handleRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return self.class_obj.handleRequest(self.node_uid, message)

    def updateRequest(self, message):
        self.logger.debug("DebugStrategy.updateRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return self.class_obj.updateRequest(self.node_uid, message)

    def sendRequest(self, message):
        self.logger.debug("DebugStrategy.sendRequest({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return self.class_obj.sendRequest(self.node_uid, message)

    def handleResponse(self, message):
        self.logger.debug("DebugStrategy.handleResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return self.class_obj.handleResponse(self.node_uid, message)

    def updateResponse(self, message):
        self.logger.debug("DebugStrategy.updateResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return self.class_obj.updateResponse(self.node_uid, message)

    def sendResponse(self, message):
        self.logger.debug("DebugStrategy.sendResponse({:s}): processing {:s} RVF\n".format(self.name, message.metaname))
        return self.class_obj.sendResponse(self.node_uid, message)

    def getStatus(self, timeout):
        return self.class_obj.getStatus(self.node_uid, timeout)

    def getError(self, timeout):
        return self.class_obj.getError(self.node_uid, timeout)

    def apply(self, timeout=0):
        self.logger.debug("DebugStrategy.apply({:s}): processing\n".format(self.name))
        return self.class_obj.apply(self.node_uid, timeout)

    def getCallbackNames(self):
        return self.class_obj.getCallbackNames()

    def destroy(self):
        return self.class_obj.destroy(self.node_uid)

    ########### To support builders
    def register_node_uid(self, node_uid):
        self.node_uid = node_uid

    def register_dstrategy(self, dstrategy):
        self.dstrategy = dstrategy

    def register_child_uids(self, child_uids):
        self.child_uids = child_uids

    def indent(self):
        self.__indent += 4

    def dedent(self):
        self.__indent -= 4

    def writeln(self, ln):
        print("" * self.__indent, ln)

    def dump(self, indent):
        self.__indent = indent
        self.writeln("Dumping InjectionStrategy: {:s}".format(self.name))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("dstrategy = {:s}".format(self.dstrategy))
        self.writeln("parameters = {:s}".format(self.parameters))
        self.writeln("child_uids = {:s}".format(self.child_uids))
        self.writeln("module = {:s}".format(self.module))
        self.writeln("class_obj = {:s}".format(self.class_obj))
        self.class_obj.dump(self.__indent)
        self.dedent()
