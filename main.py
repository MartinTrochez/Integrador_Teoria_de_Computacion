"""Teoria de la Computacion - Trabajo Integrador

Tema:
- Creacion de un Interprete

Alumnos:
- Duarte, Octavio
- Trochez, Martin
"""

import logging
import dis
from ply import lex
from ply import yacc

registro_id_valor = {}

ast = []

reserved = ("INPUT", "PRINT", "STR", "LEN", "CHOP")

tokens = reserved + (
    "IDENTIFICADOR",
    "ASIGNACION",
    # tipos
    "NUMERO",
    "REAL",
    "STRING",
    # Operadores
    "IGUALDAD",
    "NOIGUALDAD",
    "MAYOR",
    "MENOR",
    "MAS",
    "MENOS",
    "MULTIPLICACION",
    "DIVISION",
    "EXPONENTE",
    # Limitadores
    "LPAR",
    "RPAR",
    "RBRACKET",
    "LBRACKET",
    "LBRACE",
    "RBRACE",
    "PUNTOCOMA",
    "COLON",
    "COMA",
    "COMENTARIO",
)


t_ASIGNACION = r":="
t_IGUALDAD = r"="
t_NOIGUALDAD = r"!="
t_MAYOR = r">"
t_MENOR = r"<"
t_MAS = r"\+"
t_MENOS = r"-"
t_MULTIPLICACION = r"\*"
t_DIVISION = r"/"
t_EXPONENTE = r"\*\*"
t_LPAR = r"\("
t_RPAR = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_COMA = r","
t_PUNTOCOMA = r";"
t_COLON = r":"
t_ignore = " \t\n"

"""
Reglas de tokenizacion
"""


def t_REAL(t):
    r"\d+(\.\d+)"
    try:
        t.value = float(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t


def t_NUMERO(t):
    r"\d+"
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t


def t_COMENTARIO(t):
    r"""\/\*([^(\/\*)(\*\/)])+\*\/"""
    return t


def t_STRING(t):
    r"\".*\" "
    t.value = t.value[1:-1]
    return t


def t_error(t):
    print(f"Token no valido {t.value[0]}")
    t.lexer.skip(1)


registro_identificadores = {}
for r in reserved:
    registro_identificadores[r.lower()] = r


def t_IDENTIFICADOR(t):
    r"[_a-zA-Z][_a-zA-Z\d]*"
    t.type = registro_identificadores.get(t.value, "IDENTIFICADOR")
    return t


"""
Reglas de gramatica
"""


def p_programa(p):
    "programa : declaraciones"
    p[0] = p[1]
    ast.append(p[0])


def p_declaraciones(p):
    """declaraciones : comentario declaraciones
    | comentario
    | declaracion
    | declaraciones comentario
    """
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = p[1]


def p_comentario(p):
    """comentario : COMENTARIO"""
    p[0] = p[1]


def p_declaracion(p):
    """declaracion : LBRACE estado RBRACE"""
    p[0] = p[1]


def p_estado(p):
    """estado : asignacion_declaracion estado
    | asignacion_declaracion
    """
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = p[1]


def p_estado_comentario(p):
    """estado : comentario estado
    | comentario
    """
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = p[1]


def p_asignacion_declaracion(p):
    """asignacion_declaracion : IDENTIFICADOR ASIGNACION E PUNTOCOMA
    | IDENTIFICADOR ASIGNACION INPUT LPAR RPAR PUNTOCOMA
    | IDENTIFICADOR ASIGNACION INPUT LPAR STRING RPAR PUNTOCOMA
    """
    if len(p) == 5:
        registro_id_valor[p[1]] = p[3]
    elif len(p) == 7:
        registro_id_valor[p[1]] = input()
    elif len(p) == 8:
        registro_id_valor[p[1]] = input(p[5])


def p_asignacion_declaracion_string(p):
    """asignacion_declaracion : PRINT LPAR STRING RPAR PUNTOCOMA"""
    p[0] = (p[1], p[3])
    print(p[3])


def p_asignacion_declaracion_identificador(p):
    """asignacion_declaracion : PRINT LPAR IDENTIFICADOR RPAR PUNTOCOMA"""
    p[0] = (p[1], p[3])
    print(registro_id_valor[p[3]])


def p_asignacion_declaracion_numero(p):
    """asignacion_declaracion : PRINT LPAR NUMERO RPAR PUNTOCOMA
    | PRINT LPAR REAL RPAR PUNTOCOMA
    """
    p[0] = (p[0], p[3])
    print(p[3])


def p_asignacion_declaracion_string_identificador(p):
    """asignacion_declaracion : PRINT LPAR STRING COMA IDENTIFICADOR RPAR PUNTOCOMA"""
    p[0] = (p[1], p[3], p[5])
    print(p[3], registro_id_valor[p[5]])


def p_asignacion_declaracion_e(p):
    """asignacion_declaracion : PRINT LPAR E RPAR PUNTOCOMA"""
    p[0] = (p[1], p[3])
    print(p[3])


def p_E(p):
    """E : expresion"""
    p[0] = p[1]


def p_E_len(p):
    """E : LEN LPAR IDENTIFICADOR RPAR"""
    p[0] = len(registro_id_valor[p[3]])


def p_E_str(p):
    """E : STR LPAR IDENTIFICADOR RPAR"""
    p[0] = str(registro_id_valor[p[3]])


def p_E_chop(p):
    """E : CHOP LPAR IDENTIFICADOR RPAR"""
    p[0] = int(registro_id_valor[p[3]])


def p_expresion(p):
    """expresion : expresion MAS expresion
    | expresion MENOS expresion
    | expresion MULTIPLICACION expresion
    | expresion DIVISION expresion
    | expresion EXPONENTE expresion"""
    if p[2] == "+":
        if p[1] == 0:
            p[0] = p[3]
        elif p[3] == 0:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[3]
    elif p[2] == "-":
        if p[1] == p[3]:
            p[0] = 0
        else:
            p[0] = p[1] - p[3]
    elif p[2] == "*":
        if p[1] == 0 or p[3] == 0:
            p[0] = 0
        elif p[1] == 1:
            p[0] = p[3]
        elif p[3] == 1:
            p[0] = p[1]
        else:
            p[0] = p[1] * p[3]
    elif p[2] == "/":
        if p[1] == 0:
            p[0] = 0
        elif p[3] == 0:
            raise ValueError("No se puede dividir por cero")
        elif p[3] == 1:
            p[0] = p[1]
        else:
            p[0] = p[1] / p[3]
    elif p[2] == "**":
        if p[3] == 0:
            p[0] = 1
        elif p[3] == 1:
            p[0] = p[1]
        else:
            p[0] = p[1] ** p[3]


def p_expresion_grupo(p):
    "expresion : LPAR expresion RPAR"
    p[0] = p[2]


def p_expresion_number(p):
    "expresion : NUMERO"
    p[0] = int(p[1])


def p_expresion_real(p):
    "expresion : REAL"
    p[0] = float(p[1])


def p_expresion_identificador(p):
    "expresion : IDENTIFICADOR"
    p[0] = registro_id_valor[p[1]]


def p_expresion_name_str(p):
    "expresion : STRING"
    p[0] = p[1]


def p_error(p):
    print(f"Syntax error at {p.value}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        filename="parselog.txt",
        filemode="w",
        format="%(filename)10s:%(lineno)4d:%(message)s",
    )
    log = logging.getLogger()
    lexer = lex.lex(debug=True, debuglog=log)

    parser = yacc.yacc(debug=True, debuglog=log)

    path_file = "./test.txt"

    contenido = open(path_file, "r")

    lines = contenido.readlines()

    contenido.close()
    data = ""
    for line in lines:
        data += line

    parser.parse(data)

    print(ast)

    print(registro_id_valor)
    # dis.dis(p_expresion)
