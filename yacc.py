import ply.yacc as yacc

from compiler import (Assignment, Call, DoBlock, Expression, Function, Guards, IfBlock)
from lex import tokens


def p_PROG(p):
    """PROG : FUNC PROG
            | FUNC"""
    p[0] = [p[1]] + p[2] if len(p) == 3 else [p[1]]


def p_FUNC(p):
    """FUNC : NAME PARMS '=' EXPR
            | NAME PARMS GUARDS"""
    if len(p) == 5:
        p[0] = Function(p[1], p[2], p[4])
    else:
        p[0] = Function(p[1], p[2], Guards(p[3]))


def p_PARMS(p):
    """PARMS : NAME PARMS
             | empty"""
    p[0] = [p[1]] + p[2] if len(p) == 3 else []


def p_GUARDS(p):
    """GUARDS : GUARD GUARDS
              | GUARD"""
    p[0] = [p[1]] + p[2] if len(p) == 3 else [p[1]]


def p_GUARD(p):
    "GUARD : '|' EXPR '=' EXPR"
    p[0] = (p[2], p[4])


def p_EXPR(p):
    """EXPR : DO '{' STMTS '}'
            | IF EXPR THEN EXPR ELSE EXPR
            | CALL"""
    if len(p) == 5:
        p[0] = Expression(DoBlock(p[3]))
    elif len(p) == 7:
        p[0] = Expression(IfBlock(p[2], p[4], p[6]))
    else:
        p[0] = Expression(p[1])


def p_STMTS(p):
    """STMTS : STMT ';' STMTS
             | EXPR"""
    p[0] = [p[1]] + p[3] if len(p) == 4 else [p[1]]


def p_STMT(p):
    """STMT : ASSG
            | EXPR"""
    p[0] = p[1]


def p_ASSG(p):
    "ASSG : NAME ASSIGN EXPR"
    p[0] = Assignment(p[1], p[3])


def p_CALL(p):
    "CALL : NAME ARGS"
    p[0] = Call(p[1], p[2])


def p_ARGS(p):
    """ARGS : ARG ARGS
            | empty"""
    p[0] = [p[1]] + p[2] if len(p) == 3 else []


def p_ARG_CALL(p):
    "ARG : '(' CALL ')'"
    p[0] = p[2]


def p_ARG_NAME(p):
    "ARG : NAME"
    p[0] = {
        "type": "NAME",
        "value": str(p[1])
    }


def p_ARG_CONST(p):
    "ARG : CONST"
    p[0] = {
        "type": "CONST",
        "value": int(p[1])
    }


def p_empty(p):
    "empty :"
    pass


def p_error(p):
    print("Syntax error in input!")


parser = yacc.yacc()
