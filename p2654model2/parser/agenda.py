#!/usr/bin/env python
"""
    Command agenda listing the current sequence of operations to execute for this test.
    Copyright (C) 2021  Bradford G. Van Treuren

    This class is used as the execution queue for the PDLInterpreter
    object in the P2564 application.  There is only one instance
    of this class instantiated in the application.  The instance is
    managed as a Singleton meta class in the design using the get_agenda()
    factory method.

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
__date__ = "2021/02/25"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


class Agenda(object):
    """
    Command agenda listing the current sequence of operations to execute for this test.

    Use: This class is used as the execution queue for the PDLInterpreter
    object in the P2564 application.  There is only one instance
    of this class instantiated in the application.  The instance is
    managed as a Singleton meta class in the design using the get_agenda()
    factory method.
    """
    inst = None

    @staticmethod
    def get_agenda():
        if Agenda.inst is None:
            Agenda.inst = Agenda()
        return Agenda.inst

    def __init__(self):
        self.commandQueue = []
        self.current = 0

    def getNumCommands(self):
        """
        Notes: The number returned is only the number of commands
        that are at the current scope level.  CompoundCommand
        objects actually contain additional commands that are
        not accounted for in this number.

        The main role of this interface is to determine if the
        execution queue is empty or how far from empty it is.

        :return: The current size of the agenda execution queue.
        """
        return len(self.commandQueue)

    def getFirstCommand(self):
        """
        Notes: This function is the first function the PDLInterpreter
        object is to call when obtaining commands to execute.

        :return: A pointer to the first command in the execution queue.
        """
        return self.commandQueue.pop(0)

    def getNextCommand(self):
        """
        Preconditions: That getFirstCommand( ) was called before this
        function is called by a client.

        Notes: The implementation of the commandQueue member is a queue that
        provides the ability to always return the command at
        the head of the queue whether it is the first call or
        the next call.

        :return: A pointer to the command that is to be executed next by the interpreter.
        """
        if len(self.commandQueue) == 0:
            return None
        return self.commandQueue.pop(0)

    def prefixCommand(self, command):
        """
        Notes: This interface is to be used when commands need to re-execute
        themselves based on a condition being true.  The type of
        command that would execute this function are
        Conditional loop commands (WHILE, REPEAT, LOOP) that
        branch execution back to a predetermined location.

        :param command: A reference to a valid command object to be executed.
        :return: True if the command was successfully placed at the head of the queue.  Otherwise, False is returned.
        """
        self.current = 0
        try:
            self.commandQueue.insert(0, command)
            self.current += 1
            return True
        except Exception as e:
            return False

    def insertAtCurrent(self, command):
        """
        Notes: This interface is used when commands have to be placed
        in the queue following the previously inserted element.
        The primary use of this function is to add the additional
        commands following the first command in a block
        of commands contained by a CompoundCommand object.
        The CompoundCommand is replaced by the commands it
        contains.  The first command is inserted into the
        agenda using the prefixCommand() function.  All other
        commands in the CompoundCommand are inserted using
        the insertAtCurrent() function.

        :param command: A reference to a valid command object to be executed.
        :return: True if the statement was inserted.  Otherwise, False.
        """
        loc = self.current
        self.current += 1
        try:
            self.commandQueue.insert(loc, command)
            return True
        except Exception as e:
            return False

    def appendCommand(self, command):
        """
        Notes: This function is used to append commands to the end of the agenda queue.

        :param command: A reference to a valid command object to be executed.
        :return: True if the command was appended to the end of the agenda. Otherwise, False is returned.
        """
        try:
            self.commandQueue.append(command)
            return True
        except Exception as e:
            return False

    def abort(self):
        """
        Postconditions: The agenda queue is empty.

        Notes: To abort execution of a PDL program, just empty the execution agenda queue.
        :return: Nothing
        """
        if len(self.commandQueue):
            self.commandQueue.clear()
