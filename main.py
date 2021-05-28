#!/usr/bin/env python
"""
    Main entry point to the p2654model2 demonstration application.
    Copyright (C) 2021  Bradford G. Van Treuren

    Main entry point to the p2654model2 demonstration application.

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


import os
import logging
from autologging import TRACE
import sys
import os

from p2654model2.builder.builder import Builder
from p2654model2.builder.configurer import Configurer
from p2654model2.builder.drivers import Drivers
from p2654model2.builder.nodecontainer import NodeContainer
from p2654model2.parser.singleton import Singleton


def main(argv):
    logging.basicConfig(filename='example.log', level=TRACE, format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    # Drivers.set_board_sim("SPITest")
    Drivers.set_board_sim("P2654Board1")
    cc = Configurer.get_configurer()
    config_file = os.path.join(os.path.dirname(__file__), "configure.json")
    cc.load(config_file)
    bldr = Builder.get_builder()
    bldr_file = os.path.join(os.path.join(os.path.dirname(__file__), "sit"), "jtagboard1.json")
    tree = bldr.build_from_file2(bldr_file)
    nc = NodeContainer.get_nodecontainer()
    nc.define_top(tree)
    tree.configure()

    tree.dump()
    nc.dump()

    ip = Singleton.get_pdl_interpreter()
    if ip.Load(argv[1]):
        exit(ip.Run("foo", []))
    ate = Drivers.get_ate()
    ate.terminate()
    ate.close()


if __name__ == '__main__':
    main(sys.argv)
