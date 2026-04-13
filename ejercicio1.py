"""
ejercicio 1 - asdr
gramática original
"""

import sys

# lexer simple
TOKENS = ['uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', '$']

tokens = []
pos = 0

def tokenize(text):
    global tokens, pos
    words = text.strip().split()
    # valida tokens de entrada
    for w in words:
        if w not in TOKENS[:-1]:
            print(f"[ERROR] Token desconocido: '{w}'")
            sys.exit(1)
    tokens = words + ['$']  # añade fin de cadena
    pos = 0

def lookahead():
    # devuelve token actual sin consumir
    return tokens[pos]

def consume(expected=None):
    global pos
    tok = tokens[pos]
    # valida coincidencia de token esperado
    if expected and tok != expected:
        print(f"[ERROR] Se esperaba '{expected}', se encontró '{tok}' (posición {pos})")
        sys.exit(1)
    pos += 1
    return tok

# gramática transformada sin recursividad izquierda
print("=" * 60)
print("GRAMÁTICA")
print("=" * 60)
print("  S  -> A Bp C")
print("  S  -> D E")
print("  A  -> dos Bp tres")
print("  A  -> ε")
print("  Bp -> cuatro C cinco Bp")
print("  Bp -> ε")
print("  C  -> seis A Bp")
print("  C  -> ε")
print("  D  -> uno A E")
print("  D  -> Bp")
print("  E  -> tres\n")

# conjuntos primeros
print("=" * 60)
print("PRIMEROS")
print("=" * 60)
PRIMEROS = {
    'S' : {'dos', 'cuatro', 'seis', 'uno', 'ε'},
    'A' : {'dos', 'ε'},
    'Bp': {'cuatro', 'ε'},
    'C' : {'seis', 'ε'},
    'D' : {'uno', 'cuatro', 'ε'},
    'E' : {'tres'},
}
for nt, pr in PRIMEROS.items():
    print(f"  PRIMEROS({nt}) = {{ {', '.join(sorted(pr))} }}")
print()

# conjuntos siguientes
print("=" * 60)
print("SIGUIENTES")
print("=" * 60)
SIGUIENTES = {
    'S' : {'$'},
    'A' : {'cuatro', 'cinco', 'seis', 'tres', '$'},
    'Bp': {'cinco', 'seis', 'tres', '$'},
    'C' : {'cinco', 'seis', 'tres', '$'},
    'D' : {'tres', '$'},
    'E' : {'$'},
}
for nt, sg in SIGUIENTES.items():
    print(f"  SIGUIENTES({nt}) = {{ {', '.join(sorted(sg))} }}")
print()

# conjuntos de predicción
print("=" * 60)
print("PREDICCIÓN")
print("=" * 60)
PREDICCION = {
    'S -> A Bp C'          : {'dos', 'cuatro', 'seis', 'cinco', 'tres', '$'},
    'S -> D E'             : {'uno', 'cuatro', 'tres', '$'},
    'A -> dos Bp tres'     : {'dos'},
    'A -> ε'               : {'cuatro', 'cinco', 'seis', 'tres', '$'},
    'Bp -> cuatro C cinco Bp': {'cuatro'},
    'Bp -> ε'              : {'cinco', 'seis', 'tres', '$'},
    'C -> seis A Bp'       : {'seis'},
    'C -> ε'               : {'cinco', 'seis', 'tres', '$'},
    'D -> uno A E'         : {'uno'},
    'D -> Bp'              : {'cuatro', 'tres', '$'},
    'E -> tres'            : {'tres'},
}
for regla, pred in PREDICCION.items():
    print(f"  PRED({regla}) = {{ {', '.join(sorted(pred))} }}")
print()

# verificación ll(1)
print("=" * 60)
print("¿ES LL(1)?")
print("=" * 60)
print("no, hay intersección en S\n")

# parser descendente
def parse_S():
    la = lookahead()
    # seleccion de producción según lookahead
    if la in ('dos', 'seis', 'cinco', '$') or la == 'cuatro':
        parse_A()
        parse_Bp()
        parse_C()
    elif la == 'uno':
        parse_D()
        parse_E()
    else:
        # caso por defecto (ε implícitos)
        parse_A()
        parse_Bp()
        parse_C()

def parse_A():
    # A -> dos Bp tres | ε
    if lookahead() == 'dos':
        consume('dos')
        parse_Bp()
        consume('tres')

def parse_Bp():
    # Bp -> cuatro C cinco Bp | ε
    if lookahead() == 'cuatro':
        consume('cuatro')
        parse_C()
        consume('cinco')
        parse_Bp()

def parse_C():
    # C -> seis A Bp | ε
    if lookahead() == 'seis':
        consume('seis')
        parse_A()
        parse_Bp()

def parse_D():
    # D -> uno A E | Bp
    if lookahead() == 'uno':
        consume('uno')
        parse_A()
        parse_E()
    else:
        parse_Bp()

def parse_E():
    # E -> tres
    consume('tres')

# pruebas
print("=" * 60)
print("ASDR")
print("=" * 60)

ejemplos = [
    "dos cuatro seis tres cinco tres",
    "uno dos tres",
    "seis cuatro cinco",
    "",
]

for ejemplo in ejemplos:
    cadena = ejemplo
    desc = cadena if cadena else "(cadena vacía)"
    print(f"Cadena: '{desc}'")
    try:
        tokenize(cadena if cadena else "")
        parse_S()
        # aceptación si se consumió toda la entrada
        if lookahead() == '$':
            print("  → ACEPTADA ✓\n")
        else:
            print(f"  → RECHAZADA desde '{lookahead()}' ✗\n")
    except SystemExit:
        print("  → RECHAZADA ✗\n")

# modo interactivo
while True:
    try:
        entrada = input("Cadena> ").strip()
    except EOFError:
        break
    if entrada.lower() in ('salir', 'exit', 'q'):
        break
    tokenize(entrada if entrada else "")
    try:
        parse_S()
        if lookahead() == '$':
            print("  → ACEPTADA ✓\n")
        else:
            print(f"  → RECHAZADA '{lookahead()}' ✗\n")
    except SystemExit:
        print("  → RECHAZADA ✗\n")
