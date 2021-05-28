#!/usr/bin/env python
"""
    Parser code for PDL Interpreter.
    Copyright (C) 2021  Bradford G. Van Treuren

    Parser code for PLY based parser to construct up an AST of PDL commands for a PDL file.

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


import ply.lex as lex
import ply.yacc as yacc
# from .model import *
from p2654model2.parser.pdlmodel import iWriteCommand, VectorId, Range, iReadCommand, iResetCommand, iProcDef, \
    ScalarArgument, NumberArgument, EnumArgument, RegisterArgument, iCallCommand, iScanCommand, \
    iApplyCommand, iNoteCommand, iOverrideScanInterfaceCommand, iClockCommand, iClockOverrideCommand, iRunLoopCommand, \
    iGetReadDataCommand, iGetMiscomparesCommand, iPrefixCommand, SetCommand, PutsCommand, CommandDefs, PDLSource, \
    Conditional, ConditionalOr, ConditionalAnd, Or, Xor, And, Equality, Relational, Shift, \
    Additive, Multiplicative, Unary, Variable, SquareBracketBlock, BraceBlock, Value, ConditionExpression, IfCommand, \
    ElseIfCommand, ElseCommand, SubStringCommand, StringLengthCommand, StringIndexCommand, ExpressionCommand, \
    StringEqualCommand, StringCompareCommand

current_filename = None


class MyLexer(object):

    keywords = ('iReset', 'iWrite', 'iRead', 'iApply', 'iScan', 'iOverrideScanInterface', 'iRunLoop',
                'on', 'off', 'sync', 'ir', 'chain_id', 'si', 'so', 'tck', 'sck',
                'iClock', 'iClockOverride', 'iProc', 'iCall', 'iNote',
                'iGetReadData', 'iGetMiscompares', 'iPrefix',
                'iGetStatus', 'iSetFail', 'chain', 'together', 'comment', 'status',
                'capture', 'update', 'broadcast', 'source',
                'freqmultiplier', 'freqdivider', 'time',
                'dec', 'bin', 'hex', 'quit', 'clear',
                'set', 'puts',
                'if', 'else', 'elseif', 'string', 'range',
                'length', 'index', 'expr', 'equal', 'compare', 'nocase', 'nonewline',
                # 'while', 'for', 'assert', 'do',
                # 'break', 'continue', 'return',
    )

    tokens = [
        'TCL_HEX_NUMBER',
        'TCL_BIN_NUMBER',
        'DASH',
        'ISCAN_HEX_NUMBER',
        'ISCAN_BIN_NUMBER',
        'SCALAR_ID',
        'LBRACKET',
        'RBRACKET',
        'LPAREN',
        'RPAREN',
        'LBRACE',
        'RBRACE',
        'COLON',
        'SEMICOLON',
        'DOT',
        'DOLLAR',
        'POS_INT',
        'SL_COMMENT',
        'QUOTED',
        'EVALUE',
        'DVALUE',
        'TSUFFIX',
        'OR', 'AND',
        'EQ', 'NEQ', 'GTEQ', 'LTEQ',
        'LSHIFT', 'RSHIFT', 'RRSHIFT', 'NL', 'CRNL',
             ] + [k.upper() for k in keywords]
    # literals = '()+-*/=?:,.^|&~!=[]{};<>@%'
    #
    t_EVALUE = r'\.?[0-9][0-9eE_lLdDa-fA-F.xXpP]*'
    t_DVALUE = r'[0-9]+\.[0-9]+'
    # t_CHAR_LITERAL = r'\'([^\\\n]|(\\.))*?\''
    t_QUOTED = r'\"([^\\\n]|(\\.))*?\"'
    t_TSUFFIX = r'(s)|(ms)|(us)|(ns)|(ps)|(fs)|(as)'
    t_OR = r'\|\|'
    t_AND = '&&'

    t_EQ = '=='
    t_NEQ = '!='
    t_GTEQ = '>='
    t_LTEQ = '<='

    t_LSHIFT = '<<'
    t_RSHIFT = '>>'
    t_RRSHIFT = '>>>'

    # t_ignore_LINE_COMMENT = '//.*'
    t_ignore = ' \t\f'

    def t_BLOCK_COMMENT(self, t):
        r"""/\*(.|\n)*?\*/"""
        t.lexer.lineno += t.value.count('\n')

    def t_SCALAR_ID(self, t):
        r"""[a-zA-Z][a-zA-Z,0-9_]*"""
        if t.value in MyLexer.keywords:
            t.type = t.value.upper()
        return t

    # def t_POS_INT(self, t):
    #     r"""((((0x)|(0X))[0-9a-fA-F]+)|(((0b)|(0B))[0-1]+)|(\d+))"""
    #     # r'[0-9]+'
    #     if t.value[1] == 'x' or t.value[1] == 'X':
    #         t.value = int(t.value, 16)
    #     elif t.value[1] == 'b' or t.value[1] == 'B':
    #         t.value = int(t.value, 2)
    #     else:
    #         t.value = int(t.value)
    #     return t

    def t_TCL_HEX_NUMBER(self, t):
        r"""0[xX][0-9A-Fa-f]+"""
        t.value = int(t.value, 16)
        return t

    def t_TCL_BIN_NUMBER(self, t):
        r"""0[bB][0-1]+"""
        t.value = int(t.value, 2)
        return t

    def t_ISCAN_HEX_NUMBER(self, t):
        r"""{[ ]?0x[0-9A-Fa-f]+[ ]?}"""
        t.value = int(t.value[1:-1], 16)
        return t

    def t_POS_INT(self, t):
        r"""[0-9]+"""
        t.value = int(t.value)
        return t

    def t_ISCAN_BIN_NUMBER(self, p):
        r"""[{"][ ]?0b[0-1]+[ ]?[}"]"""
        t.value = int(t.value[1:-1], 2)
        return t

    def t_SL_COMMENT(self, t):
        r"""\#.*"""
        t.lexer.lineno += 1

    t_LBRACKET = '\['
    t_RBRACKET = '\]'
    t_LPAREN = '\('
    t_RPAREN = '\)'
    t_LBRACE = '{'
    t_RBRACE = '}'
    t_COLON = ':'
    t_SEMICOLON = ';'
    t_DOT = '\.'
    t_DOLLAR = '\$'
    t_DASH = '-'

    def t_NL(self, t):
        r"""\n+"""
        t.lexer.lineno += len(t.value)
        return t

    def t_CRNL(self, t):
        r"""(\r\n)+"""
        t.lexer.lineno += len(t.value)
        return t

    def t_error(self, t):
        print("Illegal character '{}' ({}) in line {}".format(t.value[0], hex(ord(t.value[0])), t.lexer.lineno))
        t.lexer.skip(1)


class ExpressionParser(object):
    def p_expression(self, p):
        """expression : conditional_expression"""
        p[0] = p[1]

    def p_expression_not_name(self, p):
        """expression_not_name : conditional_expression_not_name"""
        p[0] = p[1]

    def p_conditional_expression(self, p):
        """conditional_expression : conditional_or_expression
                                  | conditional_or_expression '?' expression ':' conditional_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Conditional(p.lineno(1), p[1], p[3], p[5])

    def p_conditional_expression_not_name(self, p):
        """conditional_expression_not_name : conditional_or_expression_not_name
                                           | conditional_or_expression_not_name '?' expression ':' conditional_expression
                                           | name '?' expression ':' conditional_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Conditional(p.lineno(1), p[1], p[3], p[5])

    def binop(self, p, ctor):
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ctor(p.lineno(1), p[2], p[1], p[3])

    def p_conditional_or_expression(self, p):
        """conditional_or_expression : conditional_and_expression
                                     | conditional_or_expression OR conditional_and_expression"""
        self.binop(p, ConditionalOr)

    def p_conditional_or_expression_not_name(self, p):
        """conditional_or_expression_not_name : conditional_and_expression_not_name
                                              | conditional_or_expression_not_name OR conditional_and_expression
                                              | name OR conditional_and_expression"""
        self.binop(p, ConditionalOr)

    def p_conditional_and_expression(self, p):
        """conditional_and_expression : inclusive_or_expression
                                      | conditional_and_expression AND inclusive_or_expression"""
        self.binop(p, ConditionalAnd)

    def p_conditional_and_expression_not_name(self, p):
        """conditional_and_expression_not_name : inclusive_or_expression_not_name
                                               | conditional_and_expression_not_name AND inclusive_or_expression
                                               | name AND inclusive_or_expression"""
        self.binop(p, ConditionalAnd)

    def p_inclusive_or_expression(self, p):
        """inclusive_or_expression : exclusive_or_expression
                                   | inclusive_or_expression '|' exclusive_or_expression"""
        self.binop(p, Or)

    def p_inclusive_or_expression_not_name(self, p):
        """inclusive_or_expression_not_name : exclusive_or_expression_not_name
                                            | inclusive_or_expression_not_name '|' exclusive_or_expression
                                            | name '|' exclusive_or_expression"""
        self.binop(p, Or)

    def p_exclusive_or_expression(self, p):
        """exclusive_or_expression : and_expression
                                   | exclusive_or_expression '^' and_expression"""
        self.binop(p, Xor)

    def p_exclusive_or_expression_not_name(self, p):
        """exclusive_or_expression_not_name : and_expression_not_name
                                            | exclusive_or_expression_not_name '^' and_expression
                                            | name '^' and_expression"""
        self.binop(p, Xor)

    def p_and_expression(self, p):
        """and_expression : equality_expression
                          | and_expression '&' equality_expression"""
        self.binop(p, And)

    def p_and_expression_not_name(self, p):
        """and_expression_not_name : equality_expression_not_name
                                   | and_expression_not_name '&' equality_expression
                                   | name '&' equality_expression"""
        self.binop(p, And)

    def p_equality_expression(self, p):
        """equality_expression : relational_expression
                               | equality_expression EQ relational_expression
                               | equality_expression NEQ relational_expression"""
        self.binop(p, Equality)

    def p_equality_expression_not_name(self, p):
        """equality_expression_not_name : relational_expression_not_name
                                        | equality_expression_not_name EQ relational_expression
                                        | name EQ relational_expression
                                        | equality_expression_not_name NEQ relational_expression
                                        | name NEQ relational_expression"""
        self.binop(p, Equality)

    def p_relational_expression(self, p):
        """relational_expression : shift_expression
                                 | relational_expression '>' shift_expression
                                 | relational_expression '<' shift_expression
                                 | relational_expression GTEQ shift_expression
                                 | relational_expression LTEQ shift_expression"""
        self.binop(p, Relational)

    def p_relational_expression_not_name(self, p):
        """relational_expression_not_name : shift_expression_not_name
                                          | shift_expression_not_name '<' shift_expression
                                          | name '<' shift_expression
                                          | shift_expression_not_name '>' shift_expression
                                          | name '>' shift_expression
                                          | shift_expression_not_name GTEQ shift_expression
                                          | name GTEQ shift_expression
                                          | shift_expression_not_name LTEQ shift_expression
                                          | name LTEQ shift_expression"""
        self.binop(p, Relational)

    def p_shift_expression(self, p):
        """shift_expression : additive_expression
                            | shift_expression LSHIFT additive_expression
                            | shift_expression RSHIFT additive_expression
                            | shift_expression RRSHIFT additive_expression"""
        self.binop(p, Shift)

    def p_shift_expression_not_name(self, p):
        """shift_expression_not_name : additive_expression_not_name
                                     | shift_expression_not_name LSHIFT additive_expression
                                     | name LSHIFT additive_expression
                                     | shift_expression_not_name RSHIFT additive_expression
                                     | name RSHIFT additive_expression
                                     | shift_expression_not_name RRSHIFT additive_expression
                                     | name RRSHIFT additive_expression"""
        self.binop(p, Shift)

    def p_additive_expression(self, p):
        """additive_expression : multiplicative_expression
                               | additive_expression '+' multiplicative_expression
                               | additive_expression '-' multiplicative_expression"""
        self.binop(p, Additive)

    def p_additive_expression_not_name(self, p):
        """additive_expression_not_name : multiplicative_expression_not_name
                                        | additive_expression_not_name '+' multiplicative_expression
                                        | name '+' multiplicative_expression
                                        | additive_expression_not_name '-' multiplicative_expression
                                        | name '-' multiplicative_expression"""
        self.binop(p, Additive)

    def p_multiplicative_expression(self, p):
        """multiplicative_expression : unary_expression
                                     | multiplicative_expression '*' unary_expression
                                     | multiplicative_expression '/' unary_expression
                                     | multiplicative_expression '%' unary_expression"""
        self.binop(p, Multiplicative)

    def p_multiplicative_expression_not_name(self, p):
        """multiplicative_expression_not_name : unary_expression_not_name
                                              | multiplicative_expression_not_name '*' unary_expression
                                              | name '*' unary_expression
                                              | multiplicative_expression_not_name '/' unary_expression
                                              | name '/' unary_expression
                                              | multiplicative_expression_not_name '%' unary_expression
                                              | name '%' unary_expression"""
        self.binop(p, Multiplicative)

    def p_unary_expression(self, p):
        """unary_expression : '+' unary_expression
                            | '-' unary_expression
                            | unary_expression_not_plus_minus"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Unary(p.lineno(1), p[1], p[2])

    def p_unary_expression_not_name(self, p):
        """unary_expression_not_name : '+' unary_expression
                                     | '-' unary_expression
                                     | unary_expression_not_plus_minus_not_name"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Unary(p.lineno(1), p[1], p[2])

    def p_unary_expression_not_plus_minus(self, p):
        """unary_expression_not_plus_minus : primary
                                           | name
                                           | '~' unary_expression
                                           | '!' unary_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Unary(p.lineno(1), p[1], p[2])

    def p_unary_expression_not_plus_minus_not_name(self, p):
        """unary_expression_not_plus_minus_not_name : primary
                                                    | '~' unary_expression
                                                    | '!' unary_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Unary(p.lineno(1), p[1], p[2])

    def p_primary(self, p):
        """primary : primary_no_new_array"""
        p[0] = p[1]

    def p_primary_no_new_array1(self, p):
        """primary_no_new_array : variable_def"""
        p[0] = p[1]

    def p_primary_no_new_array2(self, p):
        """primary_no_new_array : '(' name ')'
                                | '(' expression_not_name ')' """
        p[0] = p[2]

    def p_primary_no_new_array3(self, p):
        """primary_no_new_array : scalar_id"""
        p[0] = Value(p.lineno(1), p[1])

    def p_primary_no_new_array4(self, p):
        """primary_no_new_array : QUOTED"""
        p[0] = Value(p.lineno(1), p[1])

    def p_primary_no_new_array5(self, p):
        """primary_no_new_array : POS_INT"""
        p[0] = Value(p.lineno(1), p[1])

    def p_variable_def(self, p):
        """variable_def : DOLLAR scalar_id"""
        p[0] = Variable(p.lineno(1), p[2])


class NameParser(object):
    def p_name_def(self, p):
        """name : scalar_id"""
        p[0] = Value(p.lineno(1), p[1])

    def p_vector_id1(self, p):
        """vector_id : scalar_id LBRACKET index RBRACKET"""
        p[0] = VectorId(p.lineno(1), p[1], p[3])

    def p_vector_id2(self, p):
        """vector_id : scalar_id LBRACKET range RBRACKET"""
        p[0] = VectorId(p.lineno(1), p[1], p[3])

    def p_dot_id1(self, p):
        """dot_id : scalar_id"""
        p[0] = p[1]

    # def p_dot_id2(self, p):
    #     """dot_id : scalar_id DOT scalar_id"""
    #     p[0] = p[1] + p[2] + p[3]

    def p_dot_id3(self, p):
        """dot_id : dot_id DOT scalar_id"""
        p[0] = p[1] + p[2] + p[3]

    # def p_instancePath(self, p):
    #     """instancePath : dot_id"""
    #     p[0] = p[1]

    def p_argument_ref(self, p):
        """argument_ref : DOLLAR SCALAR_ID"""
        p[0] = p[1] + p[2]

    def p_scanInterface_name1(self, p):
        """scanInterface_name : scalar_id"""
        p[0] = p[1]

    def p_scanInterface_name2(self, p):
        """scanInterface_name : dot_id"""
        p[0] = p[1]

    def p_hier_signal1(self, p):
        """hier_signal : dot_id
                       | vector_id
                       | argument_ref"""
        p[0] = p[1]

    # def p_hier_signal2(self, p):
    #     """hier_signal : instancePath DOT scalar_id"""
    #     p[0] = p[1] + p[2] + p[3]

    def p_hier_signal3(self, p):
        """hier_signal : dot_id DOT vector_id"""
        p[0] = p[1] + p[2] + p[3]

    def p_hier_signal4(self, p):
        """hier_signal : dot_id DOT argument_ref"""
        p[0] = p[1] + p[2] + p[3]

    def p_port(self, p):
        """port : hier_signal"""
        p[0] = p[1]

    def p_procName(self, p):
        """procName : scalar_id"""
        p[0] = p[1]

    def p_enum_name(self, p):
        """enum_name : scalar_id"""
        p[0] = p[1]


class LiteralParser(object):
    def p_keyword(self, p):
        """keyword : IWRITE
                   | IREAD
                   | ISCAN
                   | IRESET
                   | IPROC
                   | ICALL
                   | IAPPLY
                   | INOTE
                   | ICLOCK
                   | ICLOCKOVERRIDE
                   | IGETREADDATA
                   | IGETMISCOMPARES
                   | IGETSTATUS
                   | ISETFAIL
                   | ON
                   | OFF
                   | SYNC
                   | IPREFIX"""
        p[0] = p[1]

    def p_scalar_id(self, p):
        """scalar_id : SCALAR_ID
                     | keyword"""
        p[0] = p[1]

    def p_empty(self, p):
        """empty :"""
        pass

    def p_eoc(self, p):
        """eoc : SEMICOLON
               | NL
               | CRNL"""
        p[0] = p[1]

    def p_ws(self, p):
        """ws : NL
              | CRNL
              | empty"""
        p[0] = p[1]


class StatementParser(object):

    def p_tvalue(self, p):
        """tvalue : EVALUE TSUFFIX
                  | DVALUE TSUFFIX"""
        p[0] = (p[1], p[2])

    def p_pdl_number(self, p):
        """pdl_number : POS_INT
                      | TCL_HEX_NUMBER
                      | TCL_BIN_NUMBER
                      | argument_ref"""
        p[0] = p[1]

    def p_index(self, p):
        """index : pdl_number"""
        p[0] = p[1]

    def p_range(self, p):
        """range : index COLON index"""
        p[0] = Range(p.lineno(1), p[1], p[2])

    def p_sysClock(self, p):
        """sysClock : hier_signal"""
        p[0] = p[1]

    def p_cycleCount(self, p):
        """cycleCount : pdl_number"""
        p[0] = p[1]

    def p_sourceClock(self, p):
        """sourceClock : hier_signal"""
        p[0] = p[1]

    # def p_reg1(self, p):
    #     """reg : scalar_id"""
    #     p[0] = p[1]
    #
    # def p_reg2(self, p):
    #     """reg : dot_id"""
    #     # """reg : instancePath DOT scalar_id"""
    #     p[0] = p[1] + p[2] + p[3]

    def p_iwrite1(self, p):
        """iwrite_def : IWRITE dot_id pdl_number eoc"""
        p[0] = iWriteCommand(p.lineno(1), reg=p[2], pdl_number=p[3])

    def p_iwrite2(self, p):
        """iwrite_def : IWRITE port pdl_number eoc"""
        p[0] = iWriteCommand(p.lineno(1), port=p[2], pdl_number=p[3])

    def p_iwrite3(self, p):
        """iwrite_def : IWRITE dot_id enum_name eoc"""
        p[0] = iWriteCommand(p.lineno(1), reg=p[2], enum_name=p[3])

    def p_iwrite4(self, p):
        """iwrite_def : IWRITE port enum_name eoc"""
        p[0] = iWriteCommand(p.lineno(1), port=p[2], enum_name=p[3])

    def p_iread1(self, p):
        """iread_def : IREAD dot_id eoc"""
        p[0] = iReadCommand(p.lineno(1), reg=p[2])

    def p_iread2(self, p):
        """iread_def : IREAD port eoc"""
        p[0] = iReadCommand(p.lineno(1), port=p[2])

    def p_iread3(self, p):
        """iread_def : IREAD dot_id pdl_number eoc"""
        p[0] = iReadCommand(p.lineno(1), reg=p[2], pdl_number=p[3])

    def p_iread4(self, p):
        """iread_def : IREAD port pdl_number eoc"""
        p[0] = iReadCommand(p.lineno(1), port=p[2], pdl_number=p[3])

    def p_iread5(self, p):
        """iread_def : IREAD dot_id enum_name eoc"""
        p[0] = iReadCommand(p.lineno(1), reg=p[2], enum_name=p[3])

    def p_iread6(self, p):
        """iread_def : IREAD port enum_name eoc"""
        p[0] = iReadCommand(p.lineno(1), port=p[2], enum_name=p[3])

    def p_ireset1(self, p):
        """ireset_def : IRESET eoc"""
        p[0] = iResetCommand(p.lineno(1))

    def p_ireset2(self, p):
        """ireset_def : IRESET DASH SYNC eoc"""
        p[0] = iResetCommand(p.lineno(1), sync=True)

    def p_icall_def1(self, p):
        """icall_def : ICALL procName eoc"""
        p[0] = iCallCommand(p.lineno(1), p[2], [])

    def p_icall_def2(self, p):
        """icall_def : ICALL procName args eoc"""
        p[0] = iCallCommand(p.lineno(1), p[2], p[3])

    def p_length(self, p):
        """length : POS_INT"""
        p[0] = p[1]

    def p_chain_id(self, p):
        """chain_id : scalar_id"""
        p[0] = p[1]

    def p_iscan_def1(self, p):
        """iscan_def : ISCAN dot_id length DASH SI iscan_data eoc"""
        p[0] = iScanCommand(p.lineno(1), name=p[2], length=p[3], si=p[6])

    def p_iscan_def2(self, p):
        """iscan_def : ISCAN dot_id length DASH SO iscan_data eoc"""
        p[0] = iScanCommand(p.lineno(1), name=p[2], length=p[3], so=p[6])

    def p_iscan_def3(self, p):
        """iscan_def : ISCAN dot_id length DASH SI iscan_data DASH SO iscan_data eoc"""
        p[0] = iScanCommand(p.lineno(1), name=p[2], length=p[3], si=p[6], so=p[9])

    def p_iscan_def4(self, p):
        """iscan_def : ISCAN dot_id DASH CHAIN chain_id length DASH SI iscan_data DASH SO iscan_data eoc"""
        p[0] = iScanCommand(p.lineno(1), name=p[2], chain_id=p[5], length=p[6], si=p[9], so=p[12])

    def p_iscan_def5(self, p):
        """iscan_def : ISCAN dot_id DASH CHAIN chain_id length DASH SI iscan_data eoc"""
        p[0] = iScanCommand(p.lineno(1), name=p[2], chain_id=p[5], length=p[6], si=p[9])

    def p_iscan_def6(self, p):
        """iscan_def : ISCAN dot_id DASH CHAIN chain_id length DASH SO iscan_data eoc"""
        p[0] = iScanCommand(p.lineno(1), name=p[2], chain_id=p[5], length=p[6], so=p[9])

    def p_iscan_def7(self, p):
        """iscan_def : ISCAN DASH IR dot_id length DASH SI iscan_data eoc"""
        p[0] = iScanCommand(p.lineno(1), name=p[4], length=p[5], si=p[8], ir=True)

    def p_iscan_def8(self, p):
        """iscan_def : ISCAN DASH IR dot_id length DASH SO iscan_data eoc"""
        p[0] = iScanCommand(p.lineno(1), name=p[4], length=p[5], so=p[8], ir=True)

    def p_iscan_def9(self, p):
        """iscan_def : ISCAN DASH IR dot_id length DASH SI iscan_data DASH SO iscan_data eoc"""
        p[0] = iScanCommand(p.lineno(1), name=p[4], length=p[5], si=p[8], so=p[11], ir=True)

    def p_iscan_def10(self, p):
        """iscan_def : ISCAN DASH IR dot_id DASH CHAIN chain_id length DASH SI iscan_data DASH SO iscan_data eoc"""
        p[0] = iScanCommand(p.lineno(1), name=p[4], chain_id=p[7], length=p[8], si=p[11], so=p[14], ir=True)

    def p_iscan_def11(self, p):
        """iscan_def : ISCAN DASH IR dot_id DASH CHAIN chain_id length DASH SI iscan_data eoc"""
        p[0] = iScanCommand(p.lineno(1), name=p[4], chain_id=p[7], length=p[8], si=p[11], ir=True)

    def p_iscan_def12(self, p):
        """iscan_def : ISCAN DASH IR dot_id DASH CHAIN chain_id length DASH SO iscan_data eoc"""
        p[0] = iScanCommand(p.lineno(1), name=p[4], chain_id=p[7], length=p[8], so=p[11], ir=True)

    def p_iscan_data(self, p):
        """iscan_data : pdl_number
                      | ISCAN_HEX_NUMBER
                      | ISCAN_BIN_NUMBER"""
        p[0] = p[1]

    def p_iapply_def1(self, p):
        """iapply_def : IAPPLY eoc"""
        p[0] = iApplyCommand(p.lineno(1))

    def p_iapply_def2(self, p):
        """iapply_def : IAPPLY DASH TOGETHER eoc"""
        p[0] = iApplyCommand(p.lineno(1), together=True)

    def p_inote_def1(self, p):
        """inote_def : INOTE DASH COMMENT QUOTED eoc"""
        p[0] = iNoteCommand(p.lineno(1), comment=True, quoted=p[4])

    def p_inote_def2(self, p):
        """inote_def : INOTE DASH STATUS QUOTED eoc"""
        p[0] = iNoteCommand(p.lineno(1), status=True, quoted=p[4])

    def p_ioverridescan_def1(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1])

    def p_ioverridescan_def2(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE ON eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=True)

    def p_ioverridescan_def3(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE OFF eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=False)

    def p_ioverridescan_def4(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH UPDATE ON eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], update=True)

    def p_ioverridescan_def5(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH UPDATE OFF eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], update=False)

    def p_ioverridescan_def6(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH BROADCAST ON eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], broadcast=True)

    def p_ioverridescan_def7(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH BROADCAST OFF eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], broadcast=False)

    def p_ioverridescan_def8(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE ON DASH UPDATE ON eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=True, update=True)

    def p_ioverridescan_def9(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE OFF DASH UPDATE ON eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=False, update=True)

    def p_ioverridescan_def10(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE OFF DASH UPDATE OFF eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=False, update=False)

    def p_ioverridescan_def11(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE ON DASH UPDATE OFF eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=True, update=False)

    def p_ioverridescan_def12(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE ON DASH BROADCAST ON eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=True, broadcast=True)

    def p_ioverridescan_def13(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE OFF DASH BROADCAST ON eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=False, broadcast=True)

    def p_ioverridescan_def14(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE OFF DASH BROADCAST OFF eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=False, broadcast=False)

    def p_ioverridescan_def15(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE ON DASH BROADCAST OFF eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=True, broadcast=False)

    def p_ioverridescan_def16(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE ON DASH UPDATE OFF DASH BROADCAST ON eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=True, update=False, broadcast=True)

    def p_ioverridescan_def17(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE OFF DASH UPDATE OFF DASH BROADCAST ON eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=False, update=False, broadcast=True)

    def p_ioverridescan_def18(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE OFF DASH UPDATE OFF DASH BROADCAST OFF eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=False, update=False, broadcast=False)

    def p_ioverridescan_def19(self, p):
        """ioverridescan_def : IOVERRIDESCANINTERFACE scanInterfaceRef_list DASH CAPTURE ON DASH UPDATE OFF DASH BROADCAST OFF eoc"""
        p[0] = iOverrideScanInterfaceCommand(p.lineno(1), p[1], capture=True, update=False, broadcast=False)

    def p_scanInterfaceRef_list1(self, p):
        """scanInterfaceRef_list : scanInterfaceRef"""
        p[0] = []
        p[0].append(p[1])

    def p_scanInterfaceRef_list2(self, p):
        """scanInterfaceRef_list : scanInterfaceRef_list scanInterfaceRef"""
        p[0] = p[1].append(p[2])

    def p_scanInterfaceRef1(self, p):
        """scanInterfaceRef : dot_id"""
        p[0] = p[1]

    def p_iclock_def(self, p):
        """iclock_def : ICLOCK sysClock eoc"""
        p[0] = iClockCommand(p.lineno(1), p[2])

    def p_iclock_override_def1(self, p):
        """iclock_override_def : ICLOCKOVERRIDE sysClock eoc"""
        p[0] = iClockOverrideCommand(p.lineno(1), p[2])

    def p_iclock_override_def2(self, p):
        """iclock_override_def : ICLOCKOVERRIDE sysClock DASH SOURCE sourceClock DASH FREQMULTIPLIER POS_INT DASH FREQDIVIDER POS_INT eoc"""
        p[0] = iClockOverrideCommand(p.lineno(1), p[2], sourceClock=p[5], freqmultiplier=p[8], freqdivider=p[11])

    def p_iclock_override_def3(self, p):
        """iclock_override_def : ICLOCKOVERRIDE sysClock DASH SOURCE sourceClock DASH FREQMULTIPLIER POS_INT eoc"""
        p[0] = iClockOverrideCommand(p.lineno(1), p[2], sourceClock=p[5], freqmultiplier=p[8])

    def p_iclock_override_def4(self, p):
        """iclock_override_def : ICLOCKOVERRIDE sysClock DASH SOURCE sourceClock DASH FREQDIVIDER POS_INT eoc"""
        p[0] = iClockOverrideCommand(p.lineno(1), p[2], sourceClock=p[5], freqdivider=p[8])

    def p_iclock_override_def5(self, p):
        """iclock_override_def : ICLOCKOVERRIDE sysClock DASH FREQMULTIPLIER POS_INT DASH FREQDIVIDER POS_INT eoc"""
        p[0] = iClockOverrideCommand(p.lineno(1), p[2], freqmultiplier=p[5], freqdivider=p[8])

    def p_iclock_override_def6(self, p):
        """iclock_override_def : ICLOCKOVERRIDE sysClock DASH FREQMULTIPLIER POS_INT eoc"""
        p[0] = iClockOverrideCommand(p.lineno(1), p[2], freqmultiplier=p[5])

    def p_iclock_override_def7(self, p):
        """iclock_override_def : ICLOCKOVERRIDE sysClock DASH FREQDIVIDER POS_INT eoc"""
        p[0] = iClockOverrideCommand(p.lineno(1), p[2], freqdivider=p[5])

    def p_irunloop_def1(self, p):
        """irunloop_def : IRUNLOOP cycleCount eoc"""
        p[0] = iRunLoopCommand(p.lineno(1), cyclecount=p[2])

    def p_irunloop_def2(self, p):
        """irunloop_def : IRUNLOOP cycleCount DASH TCK eoc"""
        p[0] = iRunLoopCommand(p.lineno(1), cyclecount=p[2], tck=True)

    def p_irunloop_def3(self, p):
        """irunloop_def : IRUNLOOP cycleCount DASH SCK port eoc"""
        p[0] = iRunLoopCommand(p.lineno(1), cyclecount=p[2], sck=p[5])

    def p_irunloop_def4(self, p):
        """irunloop_def : IRUNLOOP DASH TIME tvalue eoc"""
        p[0] = iRunLoopCommand(p.lineno(1), time=p[4])

    def p_iget_read_data_def1(self, p):
        """iget_read_data_def : IGETREADDATA dot_id eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), reg=p[2])

    def p_iget_read_data_def2(self, p):
        """iget_read_data_def : IGETREADDATA port eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), port=p[2])

    def p_iget_read_data_def3(self, p):
        """iget_read_data_def : IGETREADDATA dot_id DASH DEC eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), reg=p[2], format="dec")

    def p_iget_read_data_def4(self, p):
        """iget_read_data_def : IGETREADDATA dot_id DASH BIN eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), reg=p[2], format="bin")

    def p_iget_read_data_def5(self, p):
        """iget_read_data_def : IGETREADDATA dot_id DASH HEX eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), reg=p[2], format="hex")

    def p_iget_read_data_def6(self, p):
        """iget_read_data_def : IGETREADDATA port DASH DEC eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), port=p[2], format="dec")

    def p_iget_read_data_def7(self, p):
        """iget_read_data_def : IGETREADDATA port DASH BIN eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), port=p[2], format="bin")

    def p_iget_read_data_def8(self, p):
        """iget_read_data_def : IGETREADDATA port DASH HEX eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), port=p[2], format="hex")

    def p_iget_read_data_def9(self, p):
        """iget_read_data_def : IGETREADDATA scanInterface_name eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), scanif_name=p[2])

    def p_iget_read_data_def10(self, p):
        """iget_read_data_def : IGETREADDATA scanInterface_name DASH DEC eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), scanif_name=p[2], format="dec")

    def p_iget_read_data_def11(self, p):
        """iget_read_data_def : IGETREADDATA scanInterface_name DASH BIN eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), scanif_name=p[2], format="bin")

    def p_iget_read_data_def12(self, p):
        """iget_read_data_def : IGETREADDATA scanInterface_name DASH HEX eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), scanif_name=p[2], format="hex")

    def p_iget_read_data_def13(self, p):
        """iget_read_data_def : IGETREADDATA scanInterface_name DASH CHAIN chain_id eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), scanif_name=p[2], chain_id=p[5])

    def p_iget_read_data_def14(self, p):
        """iget_read_data_def : IGETREADDATA scanInterface_name DASH CHAIN chain_id DASH DEC eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), scanif_name=p[2], chain_id=p[5], format="dec")

    def p_iget_read_data_def15(self, p):
        """iget_read_data_def : IGETREADDATA scanInterface_name DASH CHAIN chain_id DASH BIN eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), scanif_name=p[2], chain_id=p[5], format="bin")

    def p_iget_read_data_def16(self, p):
        """iget_read_data_def : IGETREADDATA scanInterface_name DASH CHAIN chain_id DASH HEX eoc"""
        p[0] = iGetReadDataCommand(p.lineno(1), scanif_name=p[2], chain_id=p[5], format="hex")

    def p_iget_miscompares_def1(self, p):
        """iget_miscompares_def : IGETMISCOMPARES dot_id eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), reg=p[2])

    def p_iget_miscompares_def2(self, p):
        """iget_miscompares_def : IGETMISCOMPARES port eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), port=p[2])

    def p_iget_miscompares_def3(self, p):
        """iget_miscompares_def : IGETMISCOMPARES dot_id DASH DEC eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), reg=p[2], format="dec")

    def p_iget_miscompares_def4(self, p):
        """iget_miscompares_def : IGETMISCOMPARES dot_id DASH BIN eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), reg=p[2], format="bin")

    def p_iget_miscompares_def5(self, p):
        """iget_miscompares_def : IGETMISCOMPARES dot_id DASH HEX eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), reg=p[2], format="hex")

    # def p_iget_miscompares_def6(self, p):
    #     """iget_miscompares_def : IGETMISCOMPARES port"""
    #     p[0] = iGetMiscomparesCommand(p.lineno(1), port=p[2])

    def p_iget_miscompares_def7(self, p):
        """iget_miscompares_def : IGETMISCOMPARES port DASH DEC eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), port=p[2], format="dec")

    def p_iget_miscompares_def8(self, p):
        """iget_miscompares_def : IGETMISCOMPARES port DASH BIN eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), port=p[2], format="bin")

    def p_iget_miscompares_def9(self, p):
        """iget_miscompares_def : IGETMISCOMPARES port DASH HEX eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), port=p[2], format="hex")

    def p_iget_miscompares_def10(self, p):
        """iget_miscompares_def : IGETMISCOMPARES scanInterface_name eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), scanif_name=p[2])

    def p_iget_miscompares_def11(self, p):
        """iget_miscompares_def : IGETMISCOMPARES scanInterface_name DASH CHAIN chain_id eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), scanif_name=p[2], chain_id=p[5])

    def p_iget_miscompares_def12(self, p):
        """iget_miscompares_def : IGETMISCOMPARES scanInterface_name DASH DEC eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), scanif_name=p[2], format="dec")

    def p_iget_miscompares_def13(self, p):
        """iget_miscompares_def : IGETMISCOMPARES scanInterface_name DASH BIN eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), scanif_name=p[2], format="bin")

    def p_iget_miscompares_def14(self, p):
        """iget_miscompares_def : IGETMISCOMPARES scanInterface_name DASH HEX eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), scanif_name=p[2], format="hex")

    def p_iget_miscompares_def15(self, p):
        """iget_miscompares_def : IGETMISCOMPARES scanInterface_name DASH CHAIN chain_id DASH DEC eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), scanif_name=p[2], chain_id=p[5], format="dec")

    def p_iget_miscompares_def16(self, p):
        """iget_miscompares_def : IGETMISCOMPARES scanInterface_name DASH CHAIN chain_id DASH BIN eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), scanif_name=p[2], chain_id=p[5], format="bin")

    def p_iget_miscompares_def17(self, p):
        """iget_miscompares_def : IGETMISCOMPARES scanInterface_name DASH CHAIN chain_id DASH HEX eoc"""
        p[0] = iGetMiscomparesCommand(p.lineno(1), scanif_name=p[2], chain_id=p[5], format="hex")

    def p_iprefix_def1(self, p):
        """iprefix_def : IPREFIX dot_id eoc"""
        p[0] = iPrefixCommand(p.lineno(1), dot_id=p[2])

    def p_iprefix_def2(self, p):
        """iprefix_def : IPREFIX DASH eoc"""
        p[0] = iPrefixCommand(p.lineno(1), dot_id="-")

    def p_set_def1(self, p):
        """set_def : SET scalar_id brace_block_def eoc"""
        p[0] = SetCommand(p.lineno(1), p[2], expression=p[3])

    def p_set_def2(self, p):
        """set_def : SET scalar_id square_bracket_block_def eoc"""
        p[0] = SetCommand(p.lineno(1), p[2], expression=p[3])

    def p_puts_def1(self, p):
        """puts_def : PUTS QUOTED eoc"""
        p[0] = PutsCommand(p.lineno(1), p[2], nonewline=False)

    def p_puts_def2(self, p):
        """puts_def : PUTS DASH NONEWLINE QUOTED eoc"""
        p[0] = PutsCommand(p.lineno(1), p[4], nonewline=True)

    def p_puts_def3(self, p):
        """puts_def : PUTS variable_def eoc"""
        p[0] = PutsCommand(p.lineno(1), p[2], nonewline=False)

    def p_puts_def4(self, p):
        """puts_def : PUTS DASH NONEWLINE variable_def eoc"""
        p[0] = PutsCommand(p.lineno(1), p[4], nonewline=True)

    def p_expr_def1(self, p):
        """expr_def : EXPR brace_block_def"""
        p[0] = ExpressionCommand(p.lineno(1), brace_block=p[2])

    def p_expr_def2(self, p):
        """expr_def : EXPR expression"""
        p[0] = ExpressionCommand(p.lineno(1), expression=p[2])

    def p_square_bracket_block_def(self, p):
        """square_bracket_block_def : LBRACKET command RBRACKET"""
        p[0] = SquareBracketBlock(p.lineno(1), p[2])

    def p_brace_block_def1(self, p):
        """brace_block_def : LBRACE ws commands ws RBRACE ws"""
        p[0] = BraceBlock(p.lineno(1), p[3])

    def p_brace_block_def2(self, p):
        """brace_block_def : LBRACE ws RBRACE ws"""
        p[0] = BraceBlock(p.lineno(1), [Value(p.lineno(1), True)])

    def p_condition_expression_def(self, p):
        """condition_expression : LBRACE ws expression ws RBRACE ws"""
        p[0] = ConditionExpression(p.lineno(1), p[3])

    def p_if_command_def1(self, p):
        """if_command_def : IF condition_expression brace_block_def elseif_command_def"""
        p[0] = IfCommand(p.lineno(1), p[2], p[3], p[4])

    def p_if_command_def2(self, p):
        """if_command_def : IF condition_expression brace_block_def else_command_def"""
        p[0] = IfCommand(p.lineno(1), p[2], p[3], p[4])

    def p_if_command_def3(self, p):
        """if_command_def : IF condition_expression brace_block_def"""
        p[0] = IfCommand(p.lineno(1), p[2], p[3], None)

    def p_elseif_command_def1(self, p):
        """elseif_command_def : ELSEIF condition_expression brace_block_def elseif_command_def"""
        p[0] = ElseIfCommand(p.lineno(1), p[2], p[3], p[4])

    def p_elseif_command_def2(self, p):
        """elseif_command_def : ELSEIF condition_expression brace_block_def else_command_def"""
        p[0] = ElseIfCommand(p.lineno(1), p[2], p[3], p[4])

    def p_elseif_command_def3(self, p):
        """elseif_command_def : ELSEIF condition_expression brace_block_def"""
        p[0] = ElseIfCommand(p.lineno(1), p[2], p[3], None)

    def p_else_command_def(self, p):
        """else_command_def : ELSE brace_block_def"""
        p[0] = ElseCommand(p.lineno(1), p[2])

    def p_string_command_def1(self, p):
        """string_command_def : STRING RANGE variable_def pdl_number pdl_number"""
        p[0] = SubStringCommand(p.lineno(1), p[3], p[4], p[5])

    def p_string_command_def2(self, p):
        """string_command_def : STRING LENGTH variable_def"""
        p[0] = StringLengthCommand(p.lineno(1), p[3])

    def p_string_command_def3(self, p):
        """string_command_def : STRING INDEX variable_def pdl_number"""
        p[0] = StringIndexCommand(p.lineno(1), p[3], p[4])

    def p_string_command_def4(self, p):
        """string_command_def : STRING EQUAL DASH NOCASE DASH LENGTH POS_INT QUOTED QUOTED"""
        p[0] = StringEqualCommand(p.lineno(1), p[8], p[9], nocase=True, length=True, posint=p[7])

    def p_string_command_def5(self, p):
        """string_command_def : STRING EQUAL DASH LENGTH POS_INT QUOTED QUOTED"""
        p[0] = StringEqualCommand(p.lineno(1), p[6], p[7], nocase=False, length=True, posint=p[5])

    def p_string_command_def6(self, p):
        """string_command_def : STRING EQUAL DASH NOCASE QUOTED QUOTED"""
        p[0] = StringEqualCommand(p.lineno(1), p[5], p[6], nocase=True, length=False, posint=0)

    def p_string_command_def7(self, p):
        """string_command_def : STRING EQUAL QUOTED QUOTED"""
        p[0] = StringEqualCommand(p.lineno(1), p[3], p[4], nocase=False, length=False, posint=0)

    def p_string_command_def8(self, p):
        """string_command_def : STRING COMPARE DASH NOCASE DASH LENGTH POS_INT QUOTED QUOTED"""
        p[0] = StringCompareCommand(p.lineno(1), p[8], p[9], nocase=True, length=True, posint=p[7])

    def p_string_command_def9(self, p):
        """string_command_def : STRING COMPARE DASH LENGTH POS_INT QUOTED QUOTED"""
        p[0] = StringCompareCommand(p.lineno(1), p[6], p[7], nocase=False, length=True, posint=p[5])

    def p_string_command_def10(self, p):
        """string_command_def : STRING COMPARE DASH NOCASE QUOTED QUOTED"""
        p[0] = StringCompareCommand(p.lineno(1), p[5], p[6], nocase=True, length=False, posint=0)

    def p_string_command_def11(self, p):
        """string_command_def : STRING COMPARE QUOTED QUOTED"""
        p[0] = StringCompareCommand(p.lineno(1), p[3], p[4], nocase=False, length=False, posint=0)

    def p_string_command_def12(self, p):
        """string_command_def : STRING EQUAL DASH NOCASE DASH LENGTH POS_INT variable_def QUOTED"""
        p[0] = StringEqualCommand(p.lineno(1), p[8], p[9], nocase=True, length=True, posint=p[7])

    def p_string_command_def13(self, p):
        """string_command_def : STRING EQUAL DASH LENGTH POS_INT variable_def QUOTED"""
        p[0] = StringEqualCommand(p.lineno(1), p[6], p[7], nocase=False, length=True, posint=p[5])

    def p_string_command_def14(self, p):
        """string_command_def : STRING EQUAL DASH NOCASE variable_def QUOTED"""
        p[0] = StringEqualCommand(p.lineno(1), p[5], p[6], nocase=True, length=False, posint=0)

    def p_string_command_def15(self, p):
        """string_command_def : STRING EQUAL variable_def QUOTED"""
        p[0] = StringEqualCommand(p.lineno(1), p[3], p[4], nocase=False, length=False, posint=0)

    def p_string_command_def16(self, p):
        """string_command_def : STRING COMPARE DASH NOCASE DASH LENGTH POS_INT variable_def QUOTED"""
        p[0] = StringCompareCommand(p.lineno(1), p[8], p[9], nocase=True, length=True, posint=p[7])

    def p_string_command_def17(self, p):
        """string_command_def : STRING COMPARE DASH LENGTH POS_INT variable_def QUOTED"""
        p[0] = StringCompareCommand(p.lineno(1), p[6], p[7], nocase=False, length=True, posint=p[5])

    def p_string_command_def18(self, p):
        """string_command_def : STRING COMPARE DASH NOCASE variable_def QUOTED"""
        p[0] = StringCompareCommand(p.lineno(1), p[5], p[6], nocase=True, length=False, posint=0)

    def p_string_command_def19(self, p):
        """string_command_def : STRING COMPARE variable_def QUOTED"""
        p[0] = StringCompareCommand(p.lineno(1), p[3], p[4], nocase=False, length=False, posint=0)

    def p_string_command_def20(self, p):
        """string_command_def : STRING EQUAL DASH NOCASE DASH LENGTH POS_INT QUOTED variable_def"""
        p[0] = StringEqualCommand(p.lineno(1), p[8], p[9], nocase=True, length=True, posint=p[7])

    def p_string_command_def21(self, p):
        """string_command_def : STRING EQUAL DASH LENGTH POS_INT QUOTED variable_def"""
        p[0] = StringEqualCommand(p.lineno(1), p[6], p[7], nocase=False, length=True, posint=p[5])

    def p_string_command_def22(self, p):
        """string_command_def : STRING EQUAL DASH NOCASE QUOTED variable_def"""
        p[0] = StringEqualCommand(p.lineno(1), p[5], p[6], nocase=True, length=False, posint=0)

    def p_string_command_def23(self, p):
        """string_command_def : STRING EQUAL QUOTED variable_def"""
        p[0] = StringEqualCommand(p.lineno(1), p[3], p[4], nocase=False, length=False, posint=0)

    def p_string_command_def24(self, p):
        """string_command_def : STRING COMPARE DASH NOCASE DASH LENGTH POS_INT QUOTED variable_def"""
        p[0] = StringCompareCommand(p.lineno(1), p[8], p[9], nocase=True, length=True, posint=p[7])

    def p_string_command_def25(self, p):
        """string_command_def : STRING COMPARE DASH LENGTH POS_INT QUOTED variable_def"""
        p[0] = StringCompareCommand(p.lineno(1), p[6], p[7], nocase=False, length=True, posint=p[5])

    def p_string_command_def26(self, p):
        """string_command_def : STRING COMPARE DASH NOCASE QUOTED variable_def"""
        p[0] = StringCompareCommand(p.lineno(1), p[5], p[6], nocase=True, length=False, posint=0)

    def p_string_command_def27(self, p):
        """string_command_def : STRING COMPARE QUOTED variable_def"""
        p[0] = StringCompareCommand(p.lineno(1), p[3], p[4], nocase=False, length=False, posint=0)

    def p_string_command_def28(self, p):
        """string_command_def : STRING EQUAL DASH NOCASE DASH LENGTH POS_INT variable_def variable_def"""
        p[0] = StringEqualCommand(p.lineno(1), p[8], p[9], nocase=True, length=True, posint=p[7])

    def p_string_command_def29(self, p):
        """string_command_def : STRING EQUAL DASH LENGTH POS_INT variable_def variable_def"""
        p[0] = StringEqualCommand(p.lineno(1), p[6], p[7], nocase=False, length=True, posint=p[5])

    def p_string_command_def30(self, p):
        """string_command_def : STRING EQUAL DASH NOCASE variable_def variable_def"""
        p[0] = StringEqualCommand(p.lineno(1), p[5], p[6], nocase=True, length=False, posint=0)

    def p_string_command_def31(self, p):
        """string_command_def : STRING EQUAL variable_def variable_def"""
        p[0] = StringEqualCommand(p.lineno(1), p[3], p[4], nocase=False, length=False, posint=0)

    def p_string_command_def32(self, p):
        """string_command_def : STRING COMPARE DASH NOCASE DASH LENGTH POS_INT variable_def variable_def"""
        p[0] = StringCompareCommand(p.lineno(1), p[8], p[9], nocase=True, length=True, posint=p[7])

    def p_string_command_def33(self, p):
        """string_command_def : STRING COMPARE DASH LENGTH POS_INT variable_def variable_def"""
        p[0] = StringCompareCommand(p.lineno(1), p[6], p[7], nocase=False, length=True, posint=p[5])

    def p_string_command_def34(self, p):
        """string_command_def : STRING COMPARE DASH NOCASE variable_def variable_def"""
        p[0] = StringCompareCommand(p.lineno(1), p[5], p[6], nocase=True, length=False, posint=0)

    def p_string_command_def35(self, p):
        """string_command_def : STRING COMPARE variable_def variable_def"""
        p[0] = StringCompareCommand(p.lineno(1), p[3], p[4], nocase=False, length=False, posint=0)

    def p_command_def(self, p):
        """command : icall_def
                   | expr_def
                   | ireset_def
                   | iread_def
                   | iwrite_def
                   | iscan_def
                   | iapply_def
                   | inote_def
                   | ioverridescan_def
                   | iclock_def
                   | iclock_override_def
                   | irunloop_def
                   | iget_read_data_def
                   | iget_miscompares_def
                   | iprefix_def
                   | set_def
                   | puts_def
                   | square_bracket_block_def
                   | brace_block_def
                   | if_command_def
                   | elseif_command_def
                   | else_command_def
                   | string_command_def
                   | SL_COMMENT"""
        p[0] = p[1]

    def p_commands1(self, p):
        """commands : ws command ws"""
        p[0] = [p[2]]
        # p[0] = CommandDefs()
        # p[0].addCmdDef(p[1])

    def p_commands2(self, p):
        """commands : commands ws command ws"""
        p[1].append(p[3])
        p[0] = p[1]
        # p[0] = p[1].addCmdDef(p[2])

    def p_arguments1(self, p):
        """arguments : argument"""
        p[0] = [p[1]]

    def p_arguments2(self, p):
        """arguments : arguments argument"""
        p[0] = p[1].append(p[2])

    def p_argument1(self, p):
        """argument : scalar_id"""
        p[0] = ScalarArgument(p[1])

    def p_argument2(self, p):
        """argument : LBRACE ws argWithDefault ws RBRACE"""
        p[0] = p[3]

    def p_argWithDefault1(self, p):
        """argWithDefault : scalar_id ws pdl_number"""
        p[0] = NumberArgument(p[1], p[3])

    def p_argWithDefault2(self, p):
        """argWithDefault : scalar_id ws enum_name"""
        p[0] = EnumArgument(p[1], p[3])

    def p_argWithDefault3(self, p):
        """argWithDefault : scalar_id ws dot_id"""
        p[0] = RegisterArgument(p[1], p[3])

    def p_args(self, p):
        """args : pdl_number
                | enum_name
                | dot_id"""
        p[0] = p[1]

    def p_iproc_def1(self, p):
        """iproc_def : IPROC ws procName ws LBRACE ws RBRACE ws LBRACE ws commands RBRACE eoc"""
        global current_filename
        p[0] = iProcDef(p.lineno(1), file=current_filename, name=p[3], arguments=[], commands=p[11])

    def p_iproc_def2(self, p):
        """iproc_def : IPROC ws procName ws LBRACE ws arguments ws RBRACE ws LBRACE ws commands RBRACE eoc"""
        global current_filename
        p[0] = iProcDef(p.lineno(1), file=current_filename, name=p[3], arguments=p[7], commands=p[13])

    # def p_iproc_defs1(self, p):
    #     """iproc_defs : iproc_def"""
    #     p[0] = iProcDefs().addProcDef(p[1])
    #
    # def p_iproc_defs2(self, p):
    #     """iproc_defs : iproc_defs iproc_def"""
    #     p[0] = p[1].addProcDef(p[2])


class MyParser(ExpressionParser, NameParser, LiteralParser, StatementParser):

    tokens = MyLexer.tokens

    def p_pdl_source1(self, p):
        """pdl_source : iproc_def
                      | SL_COMMENT"""
        p[0] = [p[1]]

    def p_pdl_source2(self, p):
        """pdl_source : pdl_source iproc_def
                      | pdl_source SL_COMMENT"""
        p[0] = p[1].append(p[2])

    def p_error(self, p):
        print('error: {}'.format(p))


class Parser(object):

    def __init__(self):
        self.lexer = lex.lex(module=MyLexer(), optimize=1)
        self.parser = yacc.yacc(module=MyParser(), start='pdl_source', optimize=1)
        self.filename = None

    def tokenize_string(self, code):
        self.lexer.input(code)
        for token in self.lexer:
            print(token)

    def tokenize_file(self, _file):
        if type(_file) == str:
            _file = open(_file)
        content = ''
        for line in _file:
            content += line
        return self.tokenize_string(content)

    def parse_expression(self, code, debug=0, lineno=1):
        return self.parse_string(code, debug, lineno, prefix='--')

    def parse_statement(self, code, debug=0, lineno=1):
        return self.parse_string(code, debug, lineno, prefix='* ')

    def parse_string(self, code, debug=0, lineno=1, prefix='++'):
        self.lexer.lineno = lineno
        return self.parser.parse(prefix + code, lexer=self.lexer, debug=debug)

    def parse_file(self, _file, debug=0):
        global current_filename
        current_filename = _file
        if type(_file) == str:
            _file = open(_file)
        content = _file.read()
        return self.parse_string(content, debug=debug)


if __name__ == '__main__':
    # for testing
    lexer = lex.lex(module=MyLexer())
    parser = yacc.yacc(module=MyParser(), write_tables=0, start='pdl_source')

    expressions = [
        'iProc foo { } { iWrite BrdCtrl.U1.IR 0x01 }'
    ]

    for expr in expressions:
        print('lexing expression {}'.format(expr))
        lexer.input(expr)
        for token in lexer:
            print(token)

        print('parsing expression {}'.format(expr))
        t = parser.parse(expr, lexer=lexer, debug=1)
        print('result: {}'.format(t))
        print('--------------------------------')
