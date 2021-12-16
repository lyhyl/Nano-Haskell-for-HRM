import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lex import tokens


def p_PROG(p):
    """PROG : FUNC PROG
            | empty"""


def p_FUNC(p):
    "FUNC : NAME '=' EXP"


def p_EXP(p):
    """EXP : DO '{' STMTS '}'
           | IF COMP THEN EXP
           | IF COMP THEN EXP ELSE EXP
           | FEXP
           | COMP"""


def p_STMTS(p):
    """STMTS : STMT STMTS
             | empty"""


def p_empty(p):
    "empty :"
    pass


def p_error(p):
    print("Syntax error in input!")


parser = yacc.yacc()
