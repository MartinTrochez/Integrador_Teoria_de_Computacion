"""Teoria de la Computacion - Trabajo Integrador

Tema:
- Creacion de un Interprete

Alumnos:
- Duarte, Octavio
- Trochez, Martin
"""

from ply import lex
from ply import yacc
import sys
import logging

tokens = [
    "IDENTIFICADOR",
    # Tipos de varabiables
    "INTEGER",
    "FLOAT",
    "STRING",
    # Operaciones con varbiales
    "MAS",
    "MENOS",
    "MULTIPLICACION",
    "DIVISION",
    "DIVISIONINTEGER",
    "MODULO",
    "EXPONENTE",
    "ASIGNACION",
    "MENORQUE",
    "MENORQUEIGUAL",
    "MAYORQUE",
    "MAYORQUEIGUAL",
    "NOIGUALDAD",
    "IGUALDAD",
    "MENOSUNARY"
    # Limitadores
    "COMA",
    "PUNTOCOMA",
    "PARENTESISI",
    "PARENTESISD",
    "LLAVEI",
    "LLAVED",
    "CORCHETEI",
    "CORCHETED",
    "COMA",
]

reserved = {
    "or": "OR",
    "not": "NOT",
    "and": "AND",
    "in": "IN",
    "if": "IF",
    "while": "WHILE",
    "print": "PRINT",
    "else": "ELSE",
    "return": "RETURN",
}

tokens += list(reserved.values())


t_MAS = r"r\+"
t_MENOS = r"-"
t_MULTIPLICACION = r"\*"
t_DIVISION = r"\/"
t_DIVISIONINTEGER = r"\/\/"
t_MODULO = r"\%"
t_EXPONENTE = r"\*\*"
t_ASIGNACION = r"="
t_MENORQUE = r"<"
t_MENORQUEIGUAL = r"<="
t_MAYORQUE = r">"
t_MAYORQUEIGUAL = r">="
t_NOIGUALDAD = r"!="
t_IGUALDAD = r"=="
t_PUNTOCOMA = r";"
t_COMA = r"\,"
t_PARENTESISI = r"\("
t_PARENTESISD = r"\)"
t_LLAVEI = r"{"
t_LLAVED = r"}"
t_CORCHETEI = r"\["
t_CORCHETED = r"\]"
t_NOT = r"not"
t_AND = r"and"
t_OR = r"or"
t_IF = r"if"
t_ELSE = r"else"
t_PRINT = r"print"
t_WHILE = r"while"
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


def t_NUMBER(t):
    r"\d*\.\d+"
    t.value = float(t.value)
    return t


def t_STRING(t):
    r"\"[^\"]+\"|\"\" "
    t.value = str(t.value[1:-1])
    return t


def t_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("left", "NOT"),
    (
        "left",
        "MENORQUE",
        "MENORQUEIGUAL",
        "MAYORQUE",
        "MAYORQUEIGUAL",
        "NOIGUALDAD",
        "IGUALDAD",
    ),
    ("left", "IN"),
    ("left", "MAS", "MENOS"),
    ("left", "DIVISIONINTEGER"),
    ("left", "EXPONENTE"),
    ("left", "MULTIPLICACION", "DIVISION"),
    ("nonassoc", "PARENTESISI", "PARENTESISD"),
    ("nonassoc", "CORCHETEI", "CORCHETED"),
    ("nonassoc", "MENOSUNARY"),
)


"""Reglas Gramaticas"""


def p_programa(p):
    """programa : declaraciones"""
    p[0] = evaluador(p[1])


def p_declaraciones(p):
    """declaraciones : declaracion PUNTOCOMA declaraciones
    | bloque declaraciones
    | bucle declaraciones
    | funcion declaraciones
    | condicional declaraciones
    | vacio"""

    if len(p) == 4:
        p[0] = ("declaracion", p[1], p[2])
    elif len(p) == 3:
        p[0] = ("declaracion", p[1], p[3])
    elif (len(p) != 4) or (len(p) != 3):
        p[0] = p[1]


def p_condicional(p):
    """condicional : IF PARENTESISI expresion PARENTESISD bloque
    | IF PARENTESISI expresion PARENTESISD bloque ELSE bloque"""

    if len(p) == 6:
        p[0] = (p[1], p[3], p[5])
    elif len(p) == 8:
        p[0] = ("if_else", p[3], p[5], p[7])


def p_bucle(p):
    """bucle : WHILE PARENTESISI expresion PARENTESISD bloque"""

    p[0] = (p[1], p[3], p[5])


def p_bloque(p):
    """bloque : LLAVEI declaraciones LLAVED"""

    p[0] = p[2]


def p_declaracion(p):
    """declaracion : expresion
    | asignacion
    | imprimir
    | return"""

    p[0] = p[1]


def p_funcion(p):
    """funcion : IDENTIFICADOR PARENTESISI parametros PARENTESISD bloque
    | IDENTIFICADOR PARENTESISI PARENTESISD bloque"""

    if len(p) == 6:
        p[0] = ("def_funcion", p[1], p[3], p[5])
    elif len(p) == 5:
        p[0] = ("def_funcion", p[1], [], p[4])


def p_parametros(p):
    """parametros : parametros COMA IDENTIFICADOR
    | IDENTIFICADOR"""

    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2:
        p[0] = [p[1]]


def p_return(p):
    """return : RETURN expresion"""

    p[0] = ("retorno", p[2])


def p_funcionllamada(p):
    """funcionllamada : IDENTIFICADOR PARENTESISI arreglo PARENTESISD
    | IDENTIFICADOR PARENTESISI PARENTESISD"""

    if len(p) == 5:
        p[0] = ("llamada_funcion", p[1], p[3])
    elif len(p) == 4:
        p[0] = ("llamada_funcion", p[1], [])


def p_imprimir(p):
    """imprimir : PRINT PARENTESISI expresion PARENTESISD"""

    p[0] = (p[1], p[3])


def p_expresion(p):
    """expresion : logica
    | matemacia
    | funcionllamada
    | factor
    | arregloasignacion
    | arregloindice
    | comparasion"""

    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    elif len(p) == 2:
        p[0] = p[1]


def p_logica(p):
    """logica : NOT expresion
    | expresion AND expresion
    | expresion OR expresion
    | expresion IN expresion"""

    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = ("not", p[2])
    elif len(p) == 4:
        if p[2] == "and":
            p[0] = ("and", p[1], p[3])
        elif p[2] == "OR":
            p[0] = ("and", p[1], p[3])
        elif p[2] == "in":
            p[0] = ("in", p[1], p[3])


def p_arregloindice(p):
    """arregloindice : expresion CORCHETEI expresion CORCHETED"""

    p[0] = ("arreglo_indice", p[1], p[2])


def p_variable(p):
    """variable : IDENTIFICADOR"""

    p[0] = ("get_variable", p[1])


def p_comparasion(p):
    """comparasion : expresion MAYORQUE expresion
    | expresion MAYORQUEIGUAL expresion
    | expresion MENORQUE expresion
    | expresion MENORQUEIGUAL expresion
    | expresion IGUALDAD expresion
    | expresion NOIGUALDAD expresion"""

    p[0] = (p[2], p[1], p[3])


def p_asignacion(p):
    """asignacion : IDENTIFICADOR ASIGNACION expresion
    | expresion CORCHETEI expresion CORCHETED ASIGNACION expresion"""

    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    elif len(p) == 7:
        p[0] = ("asignar_valor_arreglo", p[1], p[3], p[6])


def p_matematica(p):
    """matemacia : expresion MULTIPLICACION expresion
    | expresion MAS expresion
    | expresion MENOS expresion
    | expresion DIVISION expresion
    | expresion DIVISIONINTEGER factor
    | expresion MODULO expresion
    | expresion EXPONENTE expresion
    | MENOS factor %prec MENOSUNARY"""

    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    elif len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = ("menos_unary", p[1], p[2])


def p_factor(p):
    """factor : PARENTESISI expresion PARENTESISD
    | INTEGER
    | FLOAT
    | STRING
    | variable"""

    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = p[2]


def p_arreglo(p):
    """arreglo : arreglohead elemento"""

    if len(p) == 3:
        p[0] = p[1] + p[2]


def p_arregloasignacion(p):
    """arregloasignacion : CORCHETEI CORCHETED
    | CORCHETEI arreglo CORCHETED"""

    if len(p) == 3:
        p[0] = []
    elif len(p) == 4:
        p[0] = p[2]


def p_elemento(p):
    """elemento : expresion"""

    p[0] = [p[1]]


def p_arreglohead(p):
    """arreglohead : arreglohead elemento COMA
    | vacio"""

    if len(p) == 4:
        p[0] = p[1] + p[2]
    elif len(p) == 2:
        p[0] = []


def p_vacio(p):
    """vacio :"""
    pass


def p_error(p):
    print(f"error {p.value}")


"""Evaluador"""


def evaluador(p):
    pass


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        filename="parselog.txt",
        filemode="w",
        format="%(filename)10s:%(lineno)4d:%(message)s",
    )
    log = logging.getLogger()
    lexer = lex.lex(debug=True, debuglog=log)
    lexer.input(
        """
            es_mayor_diez(numero) {
                if (numero > 10) {
                    return "numero es mayor a 10"
                } else {
                    return "numero es menor o igual a 10"
                }
            }

            b = 11;

            print(es_mayor_diez(b));
            """
    )
    for tok in lexer:
        print(tok)

    parser = yacc.yacc(debug=True, debuglog=log)
    resultado = parser.parse()
    print(resultado)
