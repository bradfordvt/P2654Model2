#!/usr/bin/env python
"""
    PDL Command classes.
    Copyright (C) 2021  Bradford G. Van Treuren

    Classes representing each PDL Command to be executed by the Agenda class.  The classes
    implement the Command design pattern using the execute() method to perform the desired
    command behavior.

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


# Base node
from myhdl import intbv

from p2654model2.builder.nodecontainer import NodeContainer
from p2654model2.parser.agenda import Agenda
from p2654model2.parser.symboltable import SymbolTable

import p2654model2.rvf.commands.register_pb2
import p2654model2.rvf.rvfmessage_pb2

import logging
from autologging import traced, logged


module_logger = logging.getLogger('p2654model2.parser.pdlmodel')


@logged
@traced
class SourceElement(object):
    '''
    A SourceElement is the base class for all elements that occur in a PDL
    file parsed by pdlzerolite.
    '''

    def __init__(self, lnum):
        # super(SourceElement, self).__init__()
        self._fields = []
        self.lineno = lnum

    def get_lineno(self):
        return self.lineno

    def __repr__(self):
        equals = ("{0}={1!r}".format(k, getattr(self, k))
                  for k in self._fields)
        args = ", ".join(equals)
        return "{0}({1})".format(self.__class__.__name__, args)

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def accept(self, visitor):
        """
        default implementation that visit the subnodes in the order
        they are stored in self_field
        """
        class_name = self.__class__.__name__
        visit = getattr(visitor, 'visit_' + class_name)
        if visit(self):
            for f in self._fields:
                field = getattr(self, f)
                if field:
                    if isinstance(field, list):
                        for elem in field:
                            if isinstance(elem, SourceElement):
                                elem.accept(visitor)
                    elif isinstance(field, SourceElement):
                        field.accept(visitor)
        getattr(visitor, 'leave_' + class_name)(self)


@logged
@traced
class VectorId(SourceElement):
    def __init__(self, lnum, scalar_id, index=None, range=None):
        super(VectorId, self).__init__(lnum)
        self.scalar_id = scalar_id
        self.index = index
        self.range = range


@logged
@traced
class Range(SourceElement):
    def __init__(self, lnum, start, end):
        super(Range, self).__init__(lnum)
        self.start = start
        self.end = end


@logged
@traced
class Command(SourceElement):
    """
    Description: An abstract base class defining the primitive
    interfaces for all types of statements defined in PDL.
    The design of the command inheritance structure is
    based on the work described in the "Patterns of
    Programming Languages, Volume 1" publication featuring
    the article on simple test languages that require
    flexibility for change.  It also is based on a
    multitasking state machine structure that is implemented
    by the PDLInterpreter class where each thread of execution
    is represented as a PDL statement object.  The concept
    of a multitasking state machine comes into play by
    always returning to the top level of the interpreter
    after executing a command.  The next thread (command)
    is selected from a queue of commands known as the
    Agenda.  Commands may be placed back on the queue
    by themselves if warranted.  For instance, a WHILE
    command would reload itself to the head of the
    Agenda if the conditional was still true.  When the
    interpreter fetches the next command from the agenda,
    the WHILE command is reexecuted as the current thread.

    The toAgenda() function is used to place the command
    into the agenda (execution queue) in the proper location
    as defined by the semantics of the command.

    The execute() function is used to perform the operation
    defined by the behavior of the command.  This function
    is to be defined by the specialized class.  The PDL
    interpreter executes each command using polymorphism
    by treating all commands as Command objects.  This
    is where the real flexability in the design of the
    language representation comes into play.
    """
    def __init__(self, lnum):
        super(Command, self).__init__(lnum)

    def toAgenda(self):
        a = Agenda.get_agenda()
        return a.appendCommand(self)

    def execute(self):
        raise NotImplementedError("Specialized commands must implement the execute() method!")

    def _vector_to_list(self, size, value):
        bvlist = []
        bv = intbv(value)
        words = (size + 31) // 32
        while words:
            bvlist.append(bv & 0xFFFFFFFF)
            bv = bv >> 32
            words -= 1
        return bvlist

    def ipint2int(self, val):
        v = 0
        i = 0
        for n in val:
            v = v + (n << (i * 32))
            i += 1
        return v


@logged
@traced
class iWriteCommand(Command):
    def __init__(self, lnum, reg=None, port=None, pdl_number=None, enum_name=None):
        super(iWriteCommand, self).__init__(lnum)
        self.reg = reg
        self.port = port
        if pdl_number is not None:
            self.pdl_number = intbv(pdl_number)
        else:
            self.pdl_number = None
        self.enum_name = enum_name

    def execute(self):
        nc = NodeContainer.get_nodecontainer()
        if self.reg:
            reg_inst = nc.get_node_by_path(self.reg)
            iid = reg_inst.get_command_id("WRITE")
            if iid is None:
                raise AssertionError("iWrite statement is not supported by this node ({:s}).".format(self.reg))
            else:
                if self.pdl_number is not None:
                    # if len(self.pdl_number) != reg_inst.size:
                    #     raise ValueError("pdl_number size does not match the register size.")
                    s = p2654model2.rvf.commands.register_pb2.WRITE()
                    s.IID = iid
                    s.nrbits = reg_inst.size
                    for v in self._vector_to_list(reg_inst.size, self.pdl_number):
                        s.value.append(v)
                    wrapper = p2654model2.rvf.rvfmessage_pb2.RVFCommand()
                    wrapper.IID = s.IID
                    wrapper.metaname = "WRITE"
                    wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
                    wrapper.serialized = s.SerializeToString()
                    return reg_inst.handleCommand(wrapper)
                elif self.enum_name:
                    raise NotImplementedError("enum_name is not yet implemented!")
                else:
                    raise AssertionError("A valid pdl_number must be defined.")
        elif self.port:
            raise NotImplementedError("port targets not yet supported.")
        else:
            raise AssertionError("A valid register path must be defined.")


@logged
@traced
class iReadCommand(Command):
    def __init__(self, lnum, reg=None, port=None, pdl_number=None, enum_name=None):
        super(iReadCommand, self).__init__(lnum)
        self.reg = reg
        self.port = port
        self.pdl_number = pdl_number
        self.enum_name = enum_name

    def execute(self):
        nc = NodeContainer.get_nodecontainer()
        if self.reg:
            reg_inst = nc.get_node_by_path(self.reg)
            iid = reg_inst.get_command_id("READ")
            if iid is None:
                raise AssertionError("iRead statement is not supported by this node ({:s}).".format(self.reg))
            else:
                if self.pdl_number:
                    if len(self.pdl_number) != reg_inst.size:
                        raise ValueError("pdl_number size does not match the register size.")
                    s = p2654model2.rvf.commands.register_pb2.READ()
                    s.IID = iid
                    s.nrbits = len(self.pdl_number)
                    for v in self._vector_to_list(len(self.pdl_number), self.pdl_number):
                        s.value.append(v)
                    wrapper = p2654model2.rvf.rvfmessage_pb2.RVFCommand()
                    wrapper.IID = s.IID
                    wrapper.metaname = "READ"
                    wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
                    wrapper.serialized = s.SerializeToString()
                    return reg_inst.handleCommand(wrapper)
                elif self.enum_name:
                    raise NotImplementedError("enum_name is not yet implemented!")
                else:
                    s = p2654model2.rvf.commands.register_pb2.READ()
                    s.IID = iid
                    s.nrbits = reg_inst.size
                    wrapper = p2654model2.rvf.rvfmessage_pb2.RVFCommand()
                    wrapper.IID = s.IID
                    wrapper.metaname = "READ"
                    wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
                    wrapper.serialized = s.SerializeToString()
                    return reg_inst.handleCommand(wrapper)
        elif self.port:
            raise NotImplementedError("port targets not yet supported.")
        else:
            raise AssertionError("A valid register path must be defined.")


@logged
@traced
class iGetReadDataCommand(Command):
    def __init__(self, lnum, reg=None, port=None, scanif_name=None, chain_id=None, format=None):
        super(iGetReadDataCommand, self).__init__(lnum)
        self.reg = reg
        self.port = port
        self.scanif_name = scanif_name
        self.chain_id = chain_id
        self.format = format

    def execute(self):
        nc = NodeContainer.get_nodecontainer()
        if self.reg:
            reg_inst = nc.get_node_by_path(self.reg)
            iid = reg_inst.get_command_id("GET")
            if iid is None:
                raise AssertionError("iGetReadData statement is not supported by this node ({:s}).".format(self.reg))
            else:
                s = p2654model2.rvf.commands.register_pb2.GET()
                s.IID = iid
                s.nrbits = reg_inst.size
                wrapper = p2654model2.rvf.rvfmessage_pb2.RVFCommand()
                wrapper.IID = s.IID
                wrapper.metaname = "GET"
                wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
                wrapper.serialized = s.SerializeToString()
                ret = reg_inst.handleCommand(wrapper)
                if ret:
                    v = reg_inst.get_value()
                    val = intbv(self.ipint2int(v), _nrbits=reg_inst.size)
                    symtbl = SymbolTable.get_symbol_table()
                    if self.format == "bin":
                        symtbl.set_result(bin(val))
                    elif self.format == "hex":
                        symtbl.set_result(hex(val))
                    else:
                        symtbl.set_result(str(val))
                return ret
        elif self.port:
            raise NotImplementedError("port targets not yet supported.")
        elif self.scanif_name:
            raise NotImplementedError("scanInterface_name targets not yet supported.")
        else:
            raise AssertionError("A valid register path must be defined.")


@logged
@traced
class iGetMiscomparesCommand(Command):
    def __init__(self, lnum, reg=None, port=None, scanif_name=None, chain_id=None, format=None):
        super(iGetMiscomparesCommand, self).__init__(lnum)
        self.reg = reg
        self.port = port
        self.scanif_name = scanif_name
        self.chain_id = chain_id
        self.format = format

    def execute(self):
        raise NotImplementedError("iGetMiscompares command not yet supported.")


@logged
@traced
class iResetCommand(Command):
    def __init__(self, lnum, sync=False):
        super(iResetCommand, self).__init__(lnum)
        self.sync = sync

    def execute(self):
        raise NotImplementedError("iResetCommand command not yet supported.")


@logged
@traced
class iCallCommand(Command):
    def __init__(self, lnum, proc_name, args):
        super(iCallCommand, self).__init__(lnum)
        self.proc_name = proc_name
        self.args = args

    def execute(self):
        symbtbl = SymbolTable.get_symbol_table()
        proc = None
        try:
            proc = symbtbl.get("global").get_symbol_value(self.proc_name)
        except ValueError as e:
            print(str(e))
            return False
        scope = symbtbl.create_scope()
        i = 0
        for arg in proc.arguments:
            symbtbl.create_symbol(scope, '$' + arg)
            symbtbl.set_symbol_value('$' + arg, self.args[i])
            i += 1
        # Now prefix iProc command to Agenda
        proc.toAgenda()


@logged
@traced
class iScanCommand(Command):
    def __init__(self, lnum, name=None, length=0, si=None, so=None, ir=False, chain_id=None, stable=False):
        super(iScanCommand, self).__init__(lnum)
        self.name = name
        self.length = length
        self.si = si
        self.so = so
        self.ir = ir
        self.chain_id = chain_id
        self.stable = stable

    def execute(self):
        nc = NodeContainer.get_nodecontainer()
        if self.name:
            symtbl = SymbolTable.get_symbol_table()
            prefix = symtbl.get_prefix()
            if prefix is None:
                path_name = self.name
            else:
                path_name = prefix + self.name
            reg_inst = nc.get_node_by_path(path_name)
            if self.so is not None and self.si is None:
                iid = reg_inst.get_command_iid("READ")
                if iid is None:
                    raise AssertionError("iScan statement is not supported by this node ({:s}).".format(path_name))
                if self.length:
                    s = p2654model2.rvf.commands.register_pb2.READ()
                    s.UID = reg_inst.UID
                    s.nrbits = self.length
                    for v in self._vector_to_list(self.length, self.so):
                        s.value.append(v)
                    wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
                    wrapper.UID = s.UID
                    wrapper.metaname = "READ"
                    wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
                    wrapper.serialized = s.SerializeToString()
                    return reg_inst.handleCommand(wrapper)
                else:
                    raise AssertionError("A valid length must be defined.")
            elif self.si is not None and self.so is None:
                iid = reg_inst.get_command_id("WRITE")
                if iid is None:
                    raise AssertionError("iScan statement is not supported by this node ({:s}).".format(path_name))
                if self.length:
                    s = p2654model2.rvf.commands.register_pb2.WRITE()
                    s.IID = iid
                    s.nrbits = self.length
                    for v in self._vector_to_list(self.length, self.si):
                        s.value.append(v)
                    wrapper = p2654model2.rvf.rvfmessage_pb2.RVFCommand()
                    wrapper.IID = s.IID
                    wrapper.metaname = "WRITE"
                    wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
                    wrapper.serialized = s.SerializeToString()
                    return reg_inst.handleCommand(wrapper)
                else:
                    raise AssertionError("A valid length must be defined.")
            elif self.si is not None and self.so is not None:
                iidr = reg_inst.get_command_id("READ")
                if iidr is None:
                    raise AssertionError("iScan statement is not supported by this node ({:s}).".format(path_name))
                iidw = reg_inst.get_command_id("WRITE")
                if iidw is None:
                    raise AssertionError("iScan statement is not supported by this node ({:s}).".format(path_name))
                if iidr != iidw:
                    raise AssertionError("iScan statement has conflicting injectors for this node ({:s}).".format(path_name))
                iid = iidr
                if self.length:
                    s = p2654model2.rvf.commands.register_pb2.WRITE()
                    s.IID = iid
                    s.nrbits = self.length
                    for v in self._vector_to_list(self.length, self.si):
                        s.value.append(v)
                    wrapper = p2654model2.rvf.rvfmessage_pb2.RVFCommand()
                    wrapper.IID = s.IID
                    wrapper.metaname = "WRITE"
                    wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
                    wrapper.serialized = s.SerializeToString()
                    wret = reg_inst.handleCommand(wrapper)
                    s = p2654model2.rvf.commands.register_pb2.READ()
                    s.UID = reg_inst.UID
                    s.nrbits = self.length
                    for v in self._vector_to_list(self.length, self.so):
                        s.value.append(v)
                    wrapper = p2654model2.rvf.rvfmessage_pb2.RVFMessage()
                    wrapper.UID = s.UID
                    wrapper.metaname = "READ"
                    wrapper.rvf_type = p2654model2.rvf.rvfmessage_pb2.WRAPPER
                    wrapper.serialized = s.SerializeToString()
                    rret = reg_inst.handleCommand(wrapper)
                    if rret is None or wret is None:
                        return None
                    else:
                        return wret and rret
                else:
                    raise AssertionError("A valid length must be defined.")
            else:
                raise AssertionError(
                    "iScan statement contains no scan vectors for this node ({:s}).".format(path_name))


@logged
@traced
class iApplyCommand(Command):
    def __init__(self, lnum, together=False):
        super(iApplyCommand, self).__init__(lnum)
        self.together = together

    def execute(self):
        nc = NodeContainer.get_nodecontainer()
        root_inst = nc.get_node_by_id(0)
        err = 0
        pending = 1
        while pending:
            ret = root_inst.apply(0)
            if ret == -1:
                err += 1
            elif ret == 1:
                pending = 1
            else:
                pending = 0
        if err:
            return False
        else:
            return True


        # from p2654model2.scheduler.scheduler import SchedulerFactory
        # ret = True
        # sched = SchedulerFactory.get_scheduler()
        # root_inst.apply(0)
        # while sched.is_pending():
        #     if not root_inst.apply(0):
        #         ret = False
        # return ret
        # # return root_inst.apply(0)


@logged
@traced
class iNoteCommand(Command):
    def __init__(self, lnum, comment=False, status=False, quoted=None):
        super(iNoteCommand, self).__init__(lnum)
        self.comment = comment
        self.status = status
        self.quoted = quoted

    def execute(self):
        raise NotImplementedError("iNote command is not implemented yet!")


@logged
@traced
class iOverrideScanInterfaceCommand(Command):
    def __init__(self, lnum, scanInterfaceRef_list, capture=False, update=False, broadcast=False):
        super(iOverrideScanInterfaceCommand, self).__init__(lnum)
        self.scanInterfaceRef_list = scanInterfaceRef_list
        self.capture = capture
        self.update = update
        self.broadcast = broadcast

    def execute(self):
        raise NotImplementedError("iOverrideScanInterface command is not implemented yet!")


@logged
@traced
class iClockCommand(Command):
    def __init__(self, lnum, clock):
        super(iClockCommand, self).__init__(lnum)
        self.clock = clock

    def execute(self):
        raise NotImplementedError("iClock command is not implemented yet!")


@logged
@traced
class iClockOverrideCommand(Command):
    def __init__(self, lnum, sysClock, sourceClock=None, freqmultiplier=None, freqdivider=None):
        super(iClockOverrideCommand, self).__init__(lnum)
        self.sysClock = sysClock
        self.sourceClock = sourceClock
        self.freqmultiplier = freqmultiplier
        self.freqdivider = freqdivider

    def execute(self):
        raise NotImplementedError("iClockOverride command is not implemented yet!")


@logged
@traced
class iRunLoopCommand(Command):
    def __init__(self, lnum, cyclecount=None, tck=False, sck=None, time=None):
        super(iRunLoopCommand, self).__init__(lnum)
        self.cyclecount = cyclecount
        self.tck = tck
        self.sck = sck
        self.time = time

    def execute(self):
        raise NotImplementedError("iRunLoop command is not implemented yet!")


@logged
@traced
class iPrefixCommand(Command):
    def __init__(self, lnum, dot_id=None):
        super( iPrefixCommand, self).__init__(lnum)
        self.prefix = dot_id

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        if self.prefix == "-":
            last_p = None
            p = symtbl.pop_prefix()
            while p is not None:
                last_p = symtbl.pop_prefix()
        else:
            symtbl.push_prefix(self.prefix)
        return True


@logged
@traced
class ConditionalCommand(Command):
    """
    Description: An intermediate specialized class that represents
    all conditional commands in PDL.  By this I mean
    all the commands that check some internal state of
    the PDLInterpreter during execution of the P2654
    program.  The conditional commands in PDL are:
    IF, WHILE, and FOR.
    """
    def __init__(self, lineno, cond):
        super(ConditionalCommand, self).__init__(lineno)
        self.condition = cond

    def getCondition(self):
        return self.condition

    def addCondition(self, cond):
        self.condition = cond


@logged
@traced
class CompoundCommand(ConditionalCommand):
    """
    Description: An intermediate specialized class for all types
    of compound commands.  By compound command I mean
    commands that contain other command groups.  In PDL,
    the compound commands are: IF, WHILE, and FOR.
    """
    def __init__(self, lineno, cond, body):
        super(CompoundCommand, self).__init__(lineno, cond)
        self.body = body
        # self.subCommands = []

    def execute(self):
        """
        Notes: The purpose of this interface is not to apply something
        to the hardware under test, but to perform the necessary
        setup for the next flow of control.  Basically, it
        replaces the compound command location (top of the queue)
        with all the commands that are contained in the
        command block.  If a compound command is one of the
        commands in the block, only the compound command
        is added as the command and not expanded at this time.
        When the contained compound command is executed, the
        expansion of that command will take place then.

        :return: True if the statements were successfully placed at the beginning of the Agenda. Otherwise, False is returned.
        """
        # ret = True
        return self.body.execute()
        # symtbl = SymbolTable.get_symbol_table()
        # commands = symtbl.get_result()
        # if len(commands):
        #     liter = iter(commands)
        #     cmd = next(liter)
        #     a = Agenda.get_agenda()
        #     ret = a.prefixCommand(cmd)
        #     cmd = next(liter)
        #     while ret and cmd is not None:
        #         ret = a.insertAtCurrent(cmd)
        #         cmd = next(liter)
        # return ret


@logged
@traced
class PopiProcCommand(Command):
    def __init__(self, lineno, proc_name):
        super(PopiProcCommand, self).__init__(lineno)
        self.proc_name = proc_name

    def toAgenda(self):
        a = Agenda.get_agenda()
        a.insertAtCurrent(self)

    def execute(self):
        symbtbl = SymbolTable.get_symbol_table()
        symbtbl.delete_scope()
        return True


@logged
@traced
class SetCommand(Command):
    def __init__(self, lnum, var_name, expression=None):
        super(SetCommand, self).__init__(lnum)
        self.var_name = var_name
        self.expression = expression

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        self.expression.execute()
        result = symtbl.get_result()
        try:
            symtbl.set_symbol_value(self.var_name, result)
        except ValueError as e:
            symtbl.create_symbol(symtbl.get_scope(), self.var_name)
            symtbl.set_symbol_value(self.var_name, result)
        return True


@logged
@traced
class PutsCommand(Command):
    def __init__(self, lnum, string_def, nonewline=False):
        super(PutsCommand, self).__init__(lnum)
        self.string_def = string_def
        self.nonewline = nonewline

    def execute(self):
        # TBD - Access to expr processing for expressions in self.string_def before printing like Tcl does2
        if isinstance(self.string_def, str):
            result = self.string_def
        else:
            symtbl = SymbolTable.get_symbol_table()
            self.string_def.execute()
            result = symtbl.get_result()
        if self.nonewline:
            print(result, end="")
        else:
            print(result)
        return True


@logged
@traced
class ExpressionCommand(Command):
    def __init__(self, lnum, brace_block=None, expression=None):
        super(ExpressionCommand, self).__init__(lnum)
        self.brace_block = brace_block
        self.expression = expression

    def execute(self):
        if self.brace_block is not None:
            return self.brace_block.execute()
        elif self.expression is not None:
            return self.expression.execute()
        return True


@logged
@traced
class SquareBracketBlock(Command):
    def __init__(self, lnum, command):
        super(SquareBracketBlock, self).__init__(lnum)
        self.command = command

    def execute(self):
        ret = self.command.execute()
        # result is already posted in symtab.result by execute()
        return ret


@logged
@traced
class BraceBlock(Command):
    def __init__(self, lnum, commands):
        super(BraceBlock, self).__init__(lnum)
        self.commands = commands

    def execute(self):
        ret = True
        if len(self.commands) == 1:
            liter = iter(self.commands)
            cmd = next(liter)
            # a = Agenda.get_agenda()
            # ret = a.prefixCommand(cmd)
            ret = cmd.execute()
        elif len(self.commands) > 1:
            liter = iter(self.commands)
            cmd = next(liter)
            # a = Agenda.get_agenda()
            # ret = a.prefixCommand(cmd)
            ret = cmd.execute()
            if not ret:
                ret = False
            cmd = next(liter)
            while ret and cmd is not None:
                # ret = a.insertAtCurrent(cmd)
                ret = cmd.execute()
                if not ret:
                    ret = False
                cmd = next(liter)
        return ret


@logged
@traced
class IfCommand(CompoundCommand):
    def __init__(self, lnum, condition, body, elseif_cmd):
        super(IfCommand, self).__init__(lnum, condition, body)
        self.elseif_cmd = elseif_cmd

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        self.getCondition().execute()
        result = symtbl.get_result()
        ret = None
        if result:
            ret = super(IfCommand, self).execute()
        elif self.elseif_cmd is not None:
            ret = self.elseif_cmd.execute()
        return ret


@logged
@traced
class ElseIfCommand(CompoundCommand):
    def __init__(self, lnum, condition, body, elseif_cmd):
        super(ElseIfCommand, self).__init__(lnum, condition)
        self.body = body
        self.elseif_cmd = elseif_cmd

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        self.getCondition().execute()
        result = symtbl.get_result()
        ret = None
        if result:
            ret = super(ElseIfCommand, self).execute()
        elif self.elseif_cmd is not None:
            ret = self.elseif_cmd.execute()
        return ret


@logged
@traced
class ElseCommand(Command):
    def __init__(self, lnum, body):
        super(ElseCommand, self).__init__(lnum)
        self.body = body

    def execute(self):
        # ret = True
        return self.body.execute()
        # symtbl = SymbolTable.get_symbol_table()
        # commands = symtbl.get_result()
        # if len(commands):
        #     liter = iter(commands)
        #     cmd = next(liter)
        #     a = Agenda.get_agenda()
        #     ret = a.prefixCommand(cmd)
        #     cmd = next(liter)
        #     while ret and cmd is not None:
        #         ret = a.insertAtCurrent(cmd)
        #         cmd = next(liter)
        # return ret


@logged
@traced
class SubStringCommand(Command):
    def __init__(self, lnum, str, start, end):
        super(SubStringCommand, self).__init__(lnum)
        self.str = str
        self.start = start
        self.end = end

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        self.str.execute()
        result = symtbl.get_result()
        # s = result.get_value()
        # subs = s[self.start:self.end+1]
        subs = result[self.start:self.end+1]
        symtbl.set_result(Value(self.str.get_lineno(), subs))
        return True


@logged
@traced
class StringLengthCommand(Command):
    def __init__(self, lnum, str):
        super(StringLengthCommand, self).__init__(lnum)
        self.str = str

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        self.str.execute()
        result = symtbl.get_result()
        s = result.get_value()
        symtbl.set_result(Value(self.str.get_lineno(), len(s)))
        return True


@logged
@traced
class StringIndexCommand(Command):
    def __init__(self, lnum, str, index):
        super(StringIndexCommand, self).__init__(lnum)
        self.str = str
        self.index = index

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        self.str.execute()
        result = symtbl.get_result()
        s = result.get_value()
        symtbl.set_result(Value(self.str.get_lineno(), s[self.index]))
        return True


@logged
@traced
class StringEqualCommand(Command):
    def __init__(self, lnum, str1, str2, nocase=False, length=False, posint=0):
        super(StringEqualCommand, self).__init__(lnum)
        self.str1 = str1
        self.str2 = str2
        self.nocase = nocase
        self.length = length
        self.posint = posint

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        if isinstance(self.str1, str):
            symtbl.set_result(Value(self.get_lineno(), self.str1))
        else:
            self.str1.execute()
        result = symtbl.get_result()
        if self.nocase:
            if isinstance(result, str):
                s1 = result.upper()
            else:
                s1 = result.get_value().upper()
        else:
            if isinstance(result, str):
                s1 = result
            elif isinstance(result, Value):
                result.execute()
                s1 = symtbl.get_result().upper()
            else:
                s1 = result.get_value()
        if isinstance(self.str2, str):
            symtbl.set_result(Value(self.get_lineno(), self.str2))
        else:
            self.str2.execute()
        result = symtbl.get_result()
        if self.nocase:
            if isinstance(result, str):
                s2 = result.upper()
            elif isinstance(result, Value):
                result.execute()
                s2 = symtbl.get_result().upper()
            else:
                s2 = result.get_value().upper()
        else:
            if isinstance(result, str):
                s2 = result.upper()
            else:
                s2 = result.get_value()
        if self.length:
            if len(s1) < self.posint:
                self.posint = len(s1)
            if len(s2) < self.posint:
                self.posint = len(s2)
            for i in range(self.posint):
                if s1[i] != s2[i]:
                    symtbl.set_result(Value(self.get_lineno(), 0))
                    return True
            symtbl.set_result(Value(self.get_lineno(), 1))
            return True
        elif s1 == s2:
            symtbl.set_result(Value(self.get_lineno(), 1))
            return True
        else:
            symtbl.set_result(Value(self.get_lineno(), 0))
            return True


@logged
@traced
class StringCompareCommand(Command):
    def __init__(self, lnum, str1, str2, nocase=False, length=False, posint=0):
        super(StringCompareCommand, self).__init__(lnum)
        self.str1 = str1
        self.str2 = str2
        self.nocase = nocase
        self.length = length
        self.posint = posint

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        self.str1.execute()
        result = symtbl.get_result()
        if self.nocase:
            s1 = result.get_value().upper()
        else:
            s1 = result.get_value()
        self.str2.execute()
        result = symtbl.get_result()
        if self.nocase:
            s2 = result.get_value().upper()
        else:
            s2 = result.get_value()
        if self.length:
            if len(s1) < self.posint:
                self.posint = len(s1)
            if len(s2) < self.posint:
                self.posint = len(s2)
            if s1[:self.posint] == s2[:self.posint]:
                symtbl.set_result(Value(self.str.get_lineno(), 0))
                return True
            elif s1[:self.posint] < s2[:self.posint]:
                symtbl.set_result(Value(self.str.get_lineno(), -1))
                return True
            elif s1[:self.posint] > s2[:self.posint]:
                symtbl.set_result(Value(self.str.get_lineno(), 1))
                return True
            else:
                raise AssertionError("Unknown comparison type")
        elif s1 == s2:
            symtbl.set_result(Value(self.str.get_lineno(), 0))
            return True
        elif s1 < s2:
            symtbl.set_result(Value(self.str.get_lineno(), -1))
            return True
        elif s1 > s2:
            symtbl.set_result(Value(self.str.get_lineno(), 1))
            return True
        else:
            raise AssertionError("Unknown comparison type")


@logged
@traced
class iProcDef(Command):
    def __init__(self, lineno, file=None, name=None, arguments=None, commands=None):
        super(iProcDef, self).__init__(lineno)
        self.file = file
        self.lineno = lineno
        self.name = name
        self.arguments = arguments
        self.commands = commands

    def toAgenda(self):
        a = Agenda.get_agenda()
        return a.prefixCommand(self)

    def execute(self):
        a = Agenda.get_agenda()
        i = True
        for cmd in self.commands:
            if i:
                if not a.prefixCommand(cmd):
                    return False  # Could not schedule this statement
                i = False
            else:
                if not a.insertAtCurrent(cmd):
                    return False
        cmd = PopiProcCommand(self.lineno, self.name)
        a.insertAtCurrent(cmd)
        return True


# class iProcDefs(object):
#     def __init__(self):
#         self.proc_defs = []
#         self.iter = None
#
#     def addProcDef(self, iproc):
#         self.proc_defs.append(iproc)
#
#     def getFirstiProcDef(self):
#         self.iter = iter(self.proc_defs)
#         return next(self.iter)
#
#     def getNextiProcDef(self):
#         if self.iter is None:
#             raise AssertionError("Must call getFirstiProcDef() first.")
#         return next(self.iter)
#
#     def getiProcDef(self, name):
#         for p in self.proc_defs:
#             if p.name == name:
#                 return p
#         return None


@logged
@traced
class CommandDefs(object):
    def __init__(self):
        self.command_defs = []
        self.iter = None

    def addCmdDef(self, iproc):
        self.command_defs.append(iproc)

    def getFirstCmdDef(self):
        self.iter = iter(self.command_defs)
        return next(self.iter)

    def getNextCmdDef(self):
        if self.iter is None:
            raise AssertionError("Must call getFirstCmdDef() first.")
        return next(self.iter)


@logged
@traced
class Argument(object):
    def __init__(self, lnum, scalar_id):
        self.scalar_id = scalar_id
        self.lineno = lnum

    def get_lineno(self):
        return self.lineno


@logged
@traced
class ScalarArgument(Argument):
    def __init__(self, lnum, scalar_id):
        super(ScalarArgument, self).__init__(lnum, scalar_id)


@logged
@traced
class NumberArgument(Argument):
    def __init__(self, lnum, scalar_id, default_value):
        super(NumberArgument, self).__init__(lnum, scalar_id)
        self.default_value = default_value


@logged
@traced
class EnumArgument(Argument):
    def __init__(self, lnum, scalar_id, default_value):
        super(EnumArgument, self).__init__(lnum, scalar_id)
        self.default_value = default_value


@logged
@traced
class RegisterArgument(Argument):
    def __init__(self, lnum, scalar_id, default_value):
        super(RegisterArgument, self).__init__(lnum, scalar_id)
        self.default_value = default_value


@logged
@traced
class PDLSource(object):
    def __init__(self):
        self.nodes = []
        self.iter = None

    def addNode(self, node):
        self.nodes.append(node)

    def getFirstNode(self):
        if self.iter is None:
            self.iter = iter(self.nodes)
        next(self.iter)

    def getNextNode(self):
        if self.iter is None:
            raise AssertionError("Must call getFirstNode() before calling getNextNode().")
        return next(self.iter)


@logged
@traced
class PDLModule(object):
    def __init__(self, name, filename, ast):
        self.name = name
        self.filename = filename
        self.ast = ast
        self.subCommands = []
        self.liter = None
        self.lineno = 0

    def getPDLName(self):
        return self.name

    def getLineno(self):
        return self.lineno

    def addCommand(self, command):
        self.subCommands.append(command)

    def getFirstCommand(self):
        if self.liter is None:
            self.liter = iter(self.subCommands)
            return next(self.liter)
        else:
            return None

    def getNextCommand(self):
        if self.liter is not None:
            return next(self.liter)
        else:
            raise AssertionError("Must call getFirstCommand() method first.")


@logged
@traced
class Expression(SourceElement):
    def __init__(self, lnum):
        super(Expression, self).__init__(lnum)
        self._fields = []

    def execute(self):
        raise NotImplementedError("Specialized expressions must implement the execute() method!")

    def eval(self, s):
        arg_list = []
        cur = None
        if isinstance(s, Command):
            ret = s.execute()
            if ret is not None:
                symtbl = SymbolTable.get_symbol_table()
                return symtbl.get_result()
        elif isinstance(s, Expression):
            ret = s.execute()
            if ret is not None:
                symtbl = SymbolTable.get_symbol_table()
                return symtbl.get_result()
        else:
            raise AssertionError("A non-expression attempting to be evaluated.")


    # def subst(self, s):
    #     if isinstance(Variable, s):
    #         symtbl = SymbolTable.get_symbol_table()
    #         return self.eval(symtbl.get_symbol_value(s.name))
    #     if isinstance(BraceBlock, s):
    #         return s.command
    #     if isinstance(SquareBracketBlock, s):
    #         return self.eval(s.command)
    #     return s
    #


@logged
@traced
class ConditionExpression(Expression):
    def __init__(self, lnum, expression):
        super(ConditionExpression, self).__init__(lnum)
        self.expression = expression

    def execute(self):
        return self.eval(self.expression)


@logged
@traced
class BinaryExpression(Expression):
    def __init__(self, lnum, operator, lhs, rhs):
        super(BinaryExpression, self).__init__(lnum)
        self._fields = ['operator', 'lhs', 'rhs']
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        self.eval(self.lhs)
        lhs = symtbl.get_result()
        self.eval(self.rhs)
        rhs = symtbl.get_result()
        if self.operator == "-":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs - rhs))
        elif self.operator == "+":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs + rhs))
        elif self.operator == "||":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs or rhs))
        elif self.operator == "&&":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs and rhs))
        elif self.operator == "|":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs | rhs))
        elif self.operator == "&":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs & rhs))
        elif self.operator == "==":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs == rhs))
        elif self.operator == "!=":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs != rhs))
        elif self.operator == ">":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs > rhs))
        elif self.operator == "<":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs < rhs))
        elif self.operator == ">=":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs >= rhs))
        elif self.operator == "<=":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs <= rhs))
        elif self.operator == "<<":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs << rhs))
        elif self.operator == ">>":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs >> rhs))
        elif self.operator == ">>>":
            raise NotImplementedError("RRSHIFT (>>>) operator is not yet supported!")
        elif self.operator == "*":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs * rhs))
        elif self.operator == "/":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs / rhs))
        elif self.operator == "%":
            symtbl.set_result(Value(self.lhs.get_lineno(), lhs % rhs))
        else:
            raise AssertionError("Unrecognized operator given to BinaryExpression!")
        return True


# class Assignment(BinaryExpression):
#     pass
#
#


@logged
@traced
class Value(Expression):
    def __init__(self, lnum, value):
        super(Value, self).__init__(lnum)
        self.value = value

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        symtbl.set_result(self.value)
        return True


@logged
@traced
class Conditional(Expression):
    def __init__(self, lnum, predicate, if_true, if_false):
        super(Conditional, self).__init__(lnum)
        self._fields = ['predicate', 'if_true', 'if_false']
        self.predicate = predicate
        self.if_true = if_true
        self.if_false = if_false

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        self.eval(self.predicate)
        result = symtbl.get_result()
        if result:
            ret = self.if_true.execute()
        else:
            ret = self.if_false.execute()
        return ret


class ConditionalOr(BinaryExpression):
    pass


class ConditionalAnd(BinaryExpression):
    pass


class Or(BinaryExpression):
    pass


class Xor(BinaryExpression):
    pass


class And(BinaryExpression):
    pass


class Equality(BinaryExpression):
    pass


class Relational(BinaryExpression):
    pass


class Shift(BinaryExpression):
    pass


class Additive(BinaryExpression):
    pass


class Multiplicative(BinaryExpression):
    pass


@logged
@traced
class Unary(Expression):
    def __init__(self, lnum, sign, expression):
        super(Unary, self).__init__(lnum)
        self._fields = ['sign', 'expression']
        self.sign = sign
        self.expression = expression

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        self.eval(self.expression)
        result = symtbl.get_result()
        if self.sign == "~":
            symtbl.set_result(Value(self.expression.get_lineno(), ~result))
        elif self.sign == "!":
            symtbl.set_result(Value(self.expression.get_lineno(), not result))
        else:
            raise AssertionError("Unsupported sign given to Unary expression!")


@logged
@traced
class ExpressionStatement(Command):
    def __init__(self, lnum, expression):
        super(ExpressionStatement, self).__init__(lnum)
        self._fields = ['expression']
        self.expression = expression

    def execute(self):
        # result already place in symtbl.result
        return self.expression.execute()


@logged
@traced
class Variable(Expression):
    def __init__(self, lnum, name):
        super(Variable, self).__init__(lnum)
        self.name = name

    def execute(self):
        symtbl = SymbolTable.get_symbol_table()
        result = symtbl.get_symbol_value(self.name)
        symtbl.set_result(result)
        return True


