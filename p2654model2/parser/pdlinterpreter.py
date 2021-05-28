#!/usr/bin/env python
"""
    Main execution engine for the P2654 application.
    Copyright (C) 2021  Bradford G. Van Treuren

    The Core Interpreter of the P2654 application that
    executes a PDL program coordinating the sequence of
    commands listed in the Agenda.

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
from enum import Enum

from p2654model2.parser.agenda import Agenda
from p2654model2.parser.pdlapi import PDLapi
from p2654model2.parser.pdlmodel import iProcDef, iWriteCommand, iReadCommand, iResetCommand, iCallCommand, \
    iScanCommand, iApplyCommand, iNoteCommand, iOverrideScanInterfaceCommand, iClockCommand, iClockOverrideCommand, \
    iRunLoopCommand, PDLModule, Command, CommandDefs
from p2654model2.parser.pdlzerolite import Parser
from p2654model2.parser.symboltable import SymbolTable


class PDLInterpreter(object):
    """
    Description: The Core Interpreter of the P2654 application that
    executes a PDL program coordinating the sequence of
    commands listed in the Agenda.

    Use: Main execution engine for the P2654 application.
    """
    inst = None

    @staticmethod
    def get_pdl_interpreter():
        if PDLInterpreter.inst is None:
            PDLInterpreter.inst = PDLInterpreter()
        return PDLInterpreter.inst

    class PDLStatus(Enum):
        PDLREADY = 0
        PDLOK = 1
        PDLWARN = 2
        PDLERR = 3

    class DIAGDETAIL(Enum):
        PDLNODIAG = 0
        PDLONFAIL = 1
        PDLALWAYS = 2

    class ERRTYPE(Enum):
        TESTFAIL = 0
        NOMEMORY = 1
        TIMEOUT = 2
        FILENOTFOUND = 3
        SYSTEMERROR = 4

    def __init__(self):
        self.failflag = False
        self.nomemflag = False
        self.timeoutflag = False
        self.filenotfoundflag = False
        self.systemerrorflag = False
        self.pdl_name = None
        self.result_directory = None
        self.instance_id = None
        self.new_rslt_dir = None
        self.needs_new_rslt_dir = False
        self.current_line = 0
        self.sscallback = None
        self.system_error = None
        self.failCount = 0
        self.maxFails = 0
        self.procs = []
        self.__api = None
        self.begin_pdl_callback = None
        self.end_pdl_callback = None
        self.pdls = []

    def Load(self, file):
        """
        Notes: This function assumes the PDL program is located in
        an ASCII readable file.  This is because the PDL parser
        implementation can only handle ASCII files as the source.

        :param file: PDL file name to execute
        :return: True if the PDL file was parsed correctly.  Otherwise, False is returned.
        """
        ret = True
        parser = Parser()
        ast = parser.parse_file(file, debug=1)
        name = os.path.basename(file).split('.')[0]
        self.pdl_name = name
        # self.__api = PDLapi(file, self)
        for obj in ast:
            if isinstance(obj, iProcDef):
                symbtbl = SymbolTable.get_symbol_table()
                proc = obj
                if proc.name in symbtbl.keys():
                    raise AssertionError("iProc ({:s}) is already defined.".format(proc.name))
                self.procs.append(proc)
                symbtbl.create_symbol("global", proc.name)
                symbtbl.set_symbol_value(proc.name, proc)
            # elif isinstance(obj, CommandDefs):
            #     cmd = obj.getFirstCmdDef()
            #     while cmd is not None:
            #         if not self.__parseCommand(obj):
            #             ret = False
            #         cmd = obj.getNextCmdDef()
            # else:
            #     raise AssertionError("Unknown object type ({:s})".format(str(type(obj))))
        pdl = PDLModule(name, file, ast)
        # self.__api.start_pdl(pdl)
        if ret and self.begin_pdl_callback is not None:
            return self.begin_pdl_callback(file)
        else:
            return ret

    # def __parseCommand(self, obj):
    #     lut = {
    #         "iWriteCommand": self.__api.start_iwrite,
    #         "iReadCommand": self.__api.start_iread,
    #         "iResetCommand": self.__api.start_ireset,
    #         "iCallCommand": self.__api.start_icall,
    #         "iScanCommand": self.__api.start_iscan,
    #         "iApplyCommand": self.__api.start_iapply,
    #         "iNoteCommand": self.__api.start_inote,
    #         "iOverrideScanInterfaceCommand": self.__api.start_ioverridescaninterface,
    #         "iClockCommand": self.__api.start_iclock,
    #         "iClockOverrideCommand": self.__api.start_iclockoverride,
    #         "iRunLoopCommand": self.__api.start_irunloop,
    #     }
    #     return lut[obj.__class__.__name__](obj)

    def Run(self, procname, topargs):
        """
        Notes: This function performs callbacks to user defined functions
        that are used to perform single step control over the PDL
        execution process.  If the callback returns False, the PDL
        program will be aborted.

        :return: True if the PDL program executed without program errors. Otherwise, False is returned.
        If a test applied by a command fails, the PDL program
        still is successful.  A False is only returned from a
        command (and thus from a command) if something went
        wrong in the application environment of the test.
        """
        # pdl = self.getPDL(self.pdl_name)
        symbtbl = SymbolTable.get_symbol_table()
        proc = None
        try:
            proc = symbtbl.get_symbol_value(procname)
        except ValueError as e:
            print(str(e))
            return False
        scope = symbtbl.create_scope()
        self.current_line = proc.lineno
        i = 0
        for arg in proc.arguments:
            symbtbl.create_symbol(scope, '$' + arg)
            symbtbl.set_symbol_value('$' + arg, topargs[i])
            i += 1
        # for cmd in proc.commands:
        #     if not cmd.toAgenda():
        #         if self.end_pdl_callback is not None:
        #             self.end_pdl_callback()
        #         return False  # Could not schedule this statement
        if not proc.toAgenda():
            if self.end_pdl_callback is not None:
                self.end_pdl_callback()
            return False  # Could not schedule this statement

        # cmd = pdl.getFirstCommand()
        # if cmd is None:
        #     if self.end_pdl_callback is not None:
        #         self.end_pdl_callback()
        #     return True
        #
        # self.current_line = cmd.getLineno()
        # if not cmd.toAgenda():
        #     if self.end_pdl_callback is not None:
        #         self.end_pdl_callback()
        #     return False  # Could not schedule this statement

        # Now schedule the remaining statements in this Flow
        # cmd = pdl.getNextCommand()
        # while cmd is not None:
        #     self.current_line = cmd.getLineno()
        #     if not cmd.toAgenda():
        #         if self.end_pdl_callback is not None:
        #             self.end_pdl_callback()
        #         return False  # Could not schedule this statement

        # This is the beginning of the real execution of each statement!
        agenda = Agenda.get_agenda()
        cmd = agenda.getFirstCommand()
        self.current_line = cmd.get_lineno()
        if cmd is None:
            if self.end_pdl_callback is not None:
                self.end_pdl_callback()
            return False  # No program to run
        # Prompt the user if in single step mode
        if self.sscallback is not None:
            if not self.sscallback(cmd.getLineno()):
                if self.end_pdl_callback is not None:
                    self.end_pdl_callback()
                return True
        self.current_line = cmd.get_lineno()

        # Now execute the first statement
        if not cmd.execute():
            if self.end_pdl_callback is not None:
                self.end_pdl_callback()
            # Here is where you could inform the user of a failed
            # execution.  Otherwise, and the better place, would
            # be to notify the user through the test step.
            return False

        if self.getMaxFails() and self.failCount >= self.getMaxFails():
            self.Stop()
        else:
            # Continue executing the rest of the statements
            cmd = agenda.getNextCommand()
            while cmd is not None:
                # Prompt the user if in single step mode
                if self.sscallback is not None:
                    if not self.sscallback(cmd.get_lineno()):
                        if self.end_pdl_callback is not None:
                            self.end_pdl_callback()
                        self.Stop()
                        break
                self.current_line = cmd.get_lineno()

                if not cmd.execute():
                    if self.end_pdl_callback is not None:
                        self.end_pdl_callback()
                    return False  # Could not execute this statement

                if self.getMaxFails() and self.failCount >= self.getMaxFails():
                    self.Stop()
                    break
                cmd = agenda.getNextCommand()
        if self.end_pdl_callback is not None:
            self.end_pdl_callback()
        return True

    def Stop(self):
        """
        Notes: By aborting the Agenda, no further commands will be processed.
        However, the hardware will be left in whatever state it was in.
        In the future, the code may wish to perform a reset of the
        hardware before exiting.

        :return: True if the PDL program was successfully terminated/aborted. Otherwise, False is returned.
        """
        agenda = Agenda.get_agenda()
        agenda.abort()
        return True

    def setPDL(self, pdlname):
        """

        :param pdlname:
        :return:
        """
        self.pdl_name = pdlname
        return True

    def setSingleStepCallback(self, new_callback):
        """
        Notes: The user's callback routine performs the user I/O to step a
        single PDL command. The user's routine may manage the
        number of steps to execute independently to what is
        controlled by the PDLInterpreter.  To do this, the callback
        routine would not query the user for information until the
        correct number of steps were executed.  After the nth step
        as executed by the callback routine, the user would then
        be prompted.

        :param new_callback:
        :return: A reference to the previously set callback.  None is returned if no callback was defined previously.
        """
        old_callback = self.sscallback
        self.sscallback = new_callback
        return old_callback

    def addPDL(self, pdl):
        """

        :param pdl:
        :return:
        """
        self.pdls.append(pdl)
        return

    def getPDL(self, name):
        """

        :param fname:
        :return:
        """
        liter = iter(self.pdls)
        pdl = next(liter)
        while pdl is not None:
            if pdl.getPDLName() == name:
                return pdl
        return None

    def setMaxFails(self, numFails):
        self.maxFails = numFails

    def getMaxFails(self):
        return self.maxFails
