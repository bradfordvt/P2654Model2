#!/usr/bin/env python
"""
    Construction API for the PDL Parser to create command objects to be played by the Agenda instance.
    Copyright (C) 2021  Bradford G. Van Treuren

    Construction API for the PDL Parser to create command objects to be played by the Agenda instance.

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
__date__ = "2021/02/22"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


class PDLapi(object):
    """

    """
    def __init__(self, fname, interp):
        """
        The P2654 Application will construct up an object using this
        constructor.

        :param fname: the name of the PDL file that is to be parsed.
        """
        self.filename = fname
        self.compoundcmds = []
        self.current_pdl = None
        self.interp = interp

    def start_pdl(self, pdl):
        self.interp.addPDL(pdl)
        self.current_pdl = pdl
        return True

    def stop_pdl(self, pdl):
        self.current_pdl = None
        return True

    def start_iwrite(self, cmd):
        return self.__addCommand(cmd)

    def start_iread(self, cmd):
        return self.__addCommand(cmd)

    def start_ireset(self, cmd):
        return self.__addCommand(cmd)

    def start_icall(self, cmd):
        return self.__addCommand(cmd)

    def start_iscan(self, cmd):
        return self.__addCommand(cmd)

    def start_iapply(self, cmd):
        return self.__addCommand(cmd)

    def start_inote(self, cmd):
        return self.__addCommand(cmd)

    def start_ioverridescaninterface(self, cmd):
        return self.__addCommand(cmd)

    def start_iclock(self, cmd):
        return self.__addCommand(cmd)

    def start_iclockoverride(self, cmd):
        return self.__addCommand(cmd)

    def start_irunloop(self, cmd):
        return self.__addCommand(cmd)

    def __addCommand(self, command):
        ret = False
        if command is None:
            ret = False
        else:
            if len(self.compoundcmds):
                ret = self.compoundcmds[-1].insertSubCmd(command)
            elif self.current_pdl is not None:
                self.current_pdl.addCommand(command)
            else:
                ret = False
        return ret
