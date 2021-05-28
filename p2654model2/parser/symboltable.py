#!/usr/bin/env python
"""
    Symbol Table for the PDL Interpreter.
    Copyright (C) 2021  Bradford G. Van Treuren

    Symbol Table for the PDL Interpreter.

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
__date__ = "2021/03/09"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"

import logging
from autologging import traced, logged


module_logger = logging.getLogger('p2654model2.parser.symboltable')


@logged
@traced
class Symbol(object):
    def __init__(self):
        self.value = None

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def get_symbol_type(self):
        return type(self.value)


@logged
@traced
class SymbolTable(object):
    """

    """
    inst = None

    @staticmethod
    def get_symbol_table():
        if SymbolTable.inst is None:
            SymbolTable.inst = SymbolTable()
        return SymbolTable.inst

    def __init__(self):
        self.symbol_table = {"global": {}}  # key is the scope (global or proc name).
        # value is tuple of dictionary with key symbol name and value tuple of attributes.
        self.scope = ["global"]
        self.prefix = [""]
        self.result = None

    def keys(self):
        return self.symbol_table.keys()

    def get_symbol_value(self, symb_name):
        scope = self.scope[-1]
        symb = self.symbol_table[scope].get(symb_name, None)
        if symb is None:
            symb = self.symbol_table["global"].get(symb_name, None)
            if symb is not None:
                return symb.get_value()
            else:
                raise ValueError("{:s} symbol cannot be found!".format(symb_name))
        else:
            return symb.get_value()

    def set_symbol_value(self, symb_name, value):
        scope = self.scope[-1]
        symb = self.symbol_table[scope].get(symb_name, None)
        if symb is None:
            symb = self.symbol_table["global"].get(symb_name, None)
            if symb is not None:
                symb.set_value(value)
            else:
                raise ValueError("{:s} symbol cannot be found!".format(symb_name))
        else:
            symb.set_value(value)

    def get_scope(self):
        return self.scope[-1]

    def create_scope(self):
        scope = str(len(self.scope))
        self.symbol_table.update({scope: {}})
        self.scope.append(scope)
        return scope

    def delete_scope(self):
        scope = str(len(self.scope) - 1)
        self.symbol_table.pop(scope, None)
        self.scope.pop()

    def create_symbol(self, scope, symb_name):
        if scope == "global":
            symb = self.symbol_table[scope].get(symb_name, None)
            if symb is not None:
                raise ValueError("{:s} symbol already exists!".format(symb_name))
            else:
                self.symbol_table["global"].update({symb_name: Symbol()})
        else:
            st = self.symbol_table.get(scope, None)
            if st is None:
                raise ValueError("{:s} scope has not yet been defined!".format(scope))
            else:
                symb = st.get(symb_name, None)
                if symb is not None:
                    raise ValueError("{:s} symbol already exists!")
                else:
                    st.update({symb_name: Symbol()})

    def delete_symbol(self, scope, symb_name):
        if scope == "global":
            self.symbol_table[scope].pop(symb_name, None)
        else:
            st = self.symbol_table.get(scope, None)
            if st is None:
                raise ValueError("{:s} scope has not yet been defined!".format(scope))
            else:
                st.pop(symb_name, None)

    def push_prefix(self, prefix):
        self.prefix.append(prefix)

    def get_prefix(self):
        if len(self.prefix) < 1:
            return None
        return self.prefix[len(self.prefix)-1]

    def pop_prefix(self):
        if len(self.prefix) < 1:
            return None
        return self.prefix.pop(len(self.prefix)-1)

    def set_result(self, result):
        self.result = result

    def get_result(self):
        return self.result

