"""Teoria de la Computacion - Trabajo Integrador

Tema:
- Creacion de un Interprete

Alumnos:
- Duarte, Octavio
- Trochez, Martin
"""

from ply import lex
from ply import yacc

tokens = [
    "IDENTIFICADOR",
    "TYPE",
    "LPAREN",
    "RPAREN",
    "COLON",
    "COMMA",
    "ARROW",
    "LBRACE",
    "RBRACE",
    "NEWLINE",
    "MAS",
    "MENOS",
    "MULTIPLICACION",
    "DIVISION",
    "ASIGNACION",
]

reserved = {
    "fun": "FUN",
    "return": "RETURN",
    "int": "INTEGER",
}
tokens += list(reserved.values())

t_LPAREN = r"\("
t_RPAREN = r"\)"
t_COLON = r":"
t_COMMA = r","
t_ARROW = r"->"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_MAS = r"\+"
t_MENOS = r"\-"
t_MULTIPLICACION = r"\*"
t_DIVISION = r"/"
t_ASIGNACION = r"="
t_ignore = " \t"


"""Reglas de Tokenizacion"""


def t_IDENTIFICADOR(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    t.type = reserved.get(t.value, "IDENTIFICADOR")
    return t


def t_INTEGER(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


precedence = (
    ("right", "ASIGNACION"),
    ("left", "MAS", "MENOS"),
    ("left", "MULTIPLICACION", "DIVISION"),
)


"""Reglas Gramaticas"""


def p_program(p):
    """program : statement_list"""
    p[0] = ("program", p[1])


def p_statement_list(p):
    """statement_list : statement_list statement
    | statement"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_statement(p):
    """statement : function
    | declaration
    | assignment
    | expression_statement"""
    p[0] = p[1]


def p_function(p):
    """function : FUN IDENTIFICADOR LPAREN parameters RPAREN ARROW tipo LBRACE statements RBRACE"""
    p[0] = ("function", p[2], p[4], p[7], p[9])


def p_parameters(p):
    """parameters : parameters COMMA parameter
    | parameter
    | empty"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2:
        p[0] = [p[1]]


def p_parameter(p):
    """parameter : IDENTIFICADOR COLON tipo"""
    p[0] = (p[1], p[3])


def p_statements(p):
    """statements : statements statement
    | statement"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [] if p[1] is None else [p[1]]


def p_declaration(p):
    """declaration : IDENTIFICADOR COLON tipo ASIGNACION expression"""
    p[0] = ("declaration", p[1], p[3], p[5])


def p_assignment(p):
    """assignment : IDENTIFICADOR ASIGNACION expression"""
    p[0] = ("assign", p[1], p[3])


def p_expression_statement(p):
    """expression_statement : expression"""
    p[0] = p[1]


def p_return_statement(p):
    """return_statement : RETURN expression"""
    p[0] = ("return", p[2])


def p_expression(p):
    """expression : expression MAS expression
    | expression MENOS expression
    | expression MULTIPLICACION expression
    | expression DIVISION expression
    | term"""
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]


def p_expression_binop(p):
    """
    expression : expression MAS expression
              | expression MENOS expression
              | expression MULTIPLICACION expression
              | expression DIVISION expression
    """
    if p[2] == "+":
        p[0] = p[1] + p[3]
    elif p[2] == "-":
        p[0] = p[1] - p[3]
    elif p[2] == "*":
        p[0] = p[1] * p[3]
    elif p[2] == "/":
        p[0] = p[1] / p[3]


def p_term(p):
    """term : INTEGER
    | IDENTIFICADOR
    | LPAREN expression RPAREN"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]


def p_empty(p):
    """empty :"""
    p[0] = None


def p_tipo(p):
    """tipo : INTEGER"""
    p[0] = p[1]


def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print(f"Syntax error at EOF")


if __name__ == "__main__":
    lexer = lex.lex()
    parser = yacc.yacc()
    # data = """
    # x: int = 2
    # y: int = 3
    # z: int = (x + y) * 2
    #
    # """
    # lexer.input(data)
    # while True:
    #     tok = lexer.token()
    #     if not tok:
    #         break
    #     print(tok)

    while True:
        try:
            s = input("calc > ")
        except EOFError:
            break
        if not s:
            continue
        yacc.parse(s + "\n")
