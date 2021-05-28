#!/usr/bin/env python
"""
    Singleton design pattern ensuring only a single instance of the PDL Parser is used by the application.
    Copyright (C) 2021  Bradford G. Van Treuren

    Singleton design pattern ensuring only a single instance of the PDL Parser is used by the application.

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
__date__ = "2021/02/21"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


from p2654model2.parser.pdlinterpreter import PDLInterpreter


class Singleton(object):
    pending = 0
    @staticmethod
    def get_pdl_interpreter():
        return PDLInterpreter.get_pdl_interpreter()

    @staticmethod
    def increment_pending():
        Singleton.pending += 1

    @staticmethod
    def decrement_pending():
        Singleton.pending -= 1

    @staticmethod
    def is_pending():
        if Singleton.pending > 0:
            return True
        return False
