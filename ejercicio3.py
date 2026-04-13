import sys

# lexer simple
TOKENS_VALIDOS = ['uno', 'dos', 'tres', 'cuatro', '$']

tokens = []
pos = 0

def tokenize(text):
    global tokens, pos
    words = text.strip().split()
    # validación de tokens
    for w in words:
        if w not in TOKENS_VALIDOS[:-1]:
            print(f"[ERROR] Token desconocido: '{w}'")
            sys.exit(1)
    tokens = words + ['$']  # fin de entrada
    pos = 0

def lookahead():
    # devuelve token actual
    return tokens[pos]

def consume(expected=None):
    global pos
    tok = tokens[pos]
    # verifica coincidencia
    if expected and tok != expected:
        print(f"[ERROR] Se esperaba '{expected}', se encontró '{tok}' (posición {pos})")
        sys.exit(1)
    pos += 1
    return tok

# gramática transformada sin recursividad izquierda
print("=" * 60)
print("GRAMÁTICA")
print("=" * 60)
print("  S  -> A B C S'")
print("  S' -> uno S'")
print("  S' -> ε")
print("  A  -> dos B C")
print("  A  -> ε")
print("  B  -> C tres")
print("  B  -> ε")
print("  C  -> cuatro B")
print("  C  -> ε\n")

# conjuntos primeros
print("=" * 60)
print("PRIMEROS")
print("=" * 60)
PRIMEROS = {
    'S' : {'dos', 'cuatro', 'ε'},
    "S'": {'uno', 'ε'},
    'A' : {'dos', 'ε'},
    'B' : {'cuatro', 'ε'},
    'C' : {'cuatro', 'ε'},
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
    "S'": {'$'},
    'A' : {'cuatro', '$'},
    'B' : {'cuatro', 'uno', '$'},
    'C' : {'uno', 'tres', '$'},
}
for nt, sg in SIGUIENTES.items():
    print(f"  SIGUIENTES({nt}) = {{ {', '.join(sorted(sg))} }}")
print()

# conjuntos de predicción
print("=" * 60)
print("PREDICCIÓN")
print("=" * 60)
PREDICCION = {
    "S  -> A B C S'"  : {'dos', 'cuatro', '$'},
    "S' -> uno S'"    : {'uno'},
    "S' -> ε"         : {'$'},
    "A  -> dos B C"   : {'dos'},
    "A  -> ε"         : {'cuatro', '$'},
    "B  -> C tres"    : {'cuatro'},
    "B  -> ε"         : {'cuatro', 'uno', '$'},
    "C  -> cuatro B"  : {'cuatro'},
    "C  -> ε"         : {'uno', 'tres', '$'},
}
for regla, pred in PREDICCION.items():
    print(f"  PRED({regla}) = {{ {', '.join(sorted(pred))} }}")
print()

# verificación ll(1)
print("=" * 60)
print("¿ES LL(1)?")
print("=" * 60)
print("no, hay conflicto en B con 'cuatro'\n")

# parser descendente
def parse_S():
    parse_A()
    parse_B()
    parse_C()
    parse_Sp()

def parse_Sp():
    # S' -> uno S' | ε
    if lookahead() == 'uno':
        consume('uno')
        parse_Sp()

def parse_A():
    # A -> dos B C | ε
    if lookahead() == 'dos':
        consume('dos')
        parse_B()
        parse_C()

def parse_B():
    la = lookahead()
    if la == 'cuatro':
        # intenta producción C tres
        parse_C()
        if lookahead() == 'tres':
            consume('tres')
        # si no hay 'tres', se interpreta como ε

def parse_C():
    # C -> cuatro B | ε
    if lookahead() == 'cuatro':
        consume('cuatro')
        parse_B()

# pruebas
print("=" * 60)
print("ASDR")
print("=" * 60)

ejemplos = [
    "dos cuatro tres",
    "cuatro tres",
    "dos cuatro tres uno uno",
    "",
]

for ejemplo in ejemplos:
    desc = f"'{ejemplo}'" if ejemplo else "'(vacía)'"
    print(f"Cadena: {desc}")
    tokenize(ejemplo if ejemplo else "")
    try:
        parse_S()
        # aceptación si no quedan tokens
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
