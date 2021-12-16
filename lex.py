import ply.lex as lex

literals = "=<>+-*(){}"

reserved = {
    'do': 'DO',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
}

tokens = [
    "ASSIGN",
    "NAME",
    "CONST",
] + list(reserved.values())


t_ASSIGN = "<-"


def t_NAME(t):
    r"[_A-Za-z]+[_0-9A-Za-z]*"
    t.type = reserved.get(t.value, "NAME")
    return t


def t_CONST(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


t_ignore = " \t"


def t_error(t):
    print(f"Illegal character '{t.value}'")
    t.lexer.skip(1)


lexer = lex.lex()
