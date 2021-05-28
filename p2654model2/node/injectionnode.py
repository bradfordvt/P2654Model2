#!/usr/bin/env python
"""
    Wrapper class to specific Injector classes.
    Copyright (C) 2021  Bradford G. Van Treuren

    The InjectionNode represents the gateway to a specific Injector plugin for the model.
    There may be zero or more InjectionNode objects associated with a single ModelNode instance.
    Each Injector is responsible for handling specific application commands for this node.
    The InjectionNode uses the defined injector to dynamically load the specialized injector
    module to be used for the associated ModelNode.

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


from p2654model2.builder.moduleloader import ModuleLoader


import logging
from autologging import traced, logged


module_logger = logging.getLogger('P2654Model2.node.injectionnode')


@logged
@traced
class InjectionNode(object):
    injid = 0
    __indent = 0

    def __init__(self, name, node_uid, transform_engine, injector, cproto):
        self.logger = logging.getLogger('P2654Model2.node.injectionnode')
        self.logger.info('Creating an instance of InjectionNode')
        self.name = name
        self.node_uid = node_uid
        self.transform_engine = transform_engine
        self.testinjection_interface = None
        self.parameters = None
        self.injector = injector
        self.cproto = cproto
        self.class_obj = None
        self.module = None
        self.iid = self.injid
        self.injid += 1

    def create(self, parameters):
        self.parameters = parameters
        # print("InjectionNode parameters = {:s}".format(str(parameters)))
        # print("InjectionNode injector = {:s}".format(str(self.injector)))
        ml = ModuleLoader.get_moduleloader()
        self.module = ml.load(self.injector, self.injector)
        if self.module is None:
            self.module = ml.load("injectorswrap", self.injector)
        if self.module is None:
            raise AssertionError("Injector class {:s} could not be found in any modules.".format(self.injector))
        # print("module.__dict__ = ", self.module.__dict__)
        cls = getattr(self.module, self.injector)
        self.class_obj = cls()
        ret = self.class_obj.create(self.name, self.node_uid, self.iid, self.injector, self.parameters, self.cproto)
        self.class_obj.set_sendRequestCallback(self.sendRequest)
        self.class_obj.set_updateDataValueCallback(self.updateDataValue)
        return ret

    def apply(self, timeout=0):
        self.logger.debug("InjectionNode.apply(): processing\n")
        return self.class_obj.apply(self.iid, timeout)

    def destroy(self):
        return self.class_obj.destroy(self.iid)

    def register_testinjection_interface(self, testinjection_interface):
        self.testinjection_interface = testinjection_interface

    def get_commands(self):
        return self.class_obj.get_commands(self.iid)

    def handleCommand(self, message):
        self.logger.debug("InjectionNode.handleCommand(): processing {:s} RVF\n".format(message.metaname))
        return self.class_obj.handleCommand(self.iid, message)

    def handleResponse(self, message):
        self.logger.debug("InjectionNode.handleResponse(): processing {:s} RVF\n".format(message.metaname))
        return self.class_obj.handleResponse(self.iid, message)

    def sendRequest(self, message):
        self.logger.debug("InjectionNode.sendRequest(): processing {:s} RVF\n".format(message.metaname))
        return self.testinjection_interface.sendRequest(message)

    def updateDataValue(self, message):
        self.logger.debug("InjectionNode.updateDataValue(): processing {:s} RVF\n".format(message.metaname))
        return self.testinjection_interface.updateDataValue(message)

    def indent(self):
        InjectionNode.__indent += 4

    def dedent(self):
        InjectionNode.__indent -= 4

    def writeln(self, ln):
        print(" " * InjectionNode.__indent, ln)

    def dump(self, indent):
        InjectionNode.__indent = indent
        self.writeln("Dumping InjectionNode: {:s}".format(str(self.name)))
        self.indent()
        self.writeln("node_uid = {:d}".format(self.node_uid))
        self.writeln("parameters = {:s}".format(str(self.parameters)))
        self.writeln("injector = {:s}".format(str(self.injector)))
        self.writeln("module = {:s}".format(str(self.module)))
        self.dedent()
