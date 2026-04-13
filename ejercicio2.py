import sys

# lexer simple
TOKENS_VALIDOS = ['uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', '$']

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
    tokens = words + ['$']  # marca fin de entrada
    pos = 0

def lookahead():
    # token actual sin consumir
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

# gramática
print("=" * 60)
print("GRAMÁTICA")
print("=" * 60)
print("  S -> B uno")
print("  S -> dos C")
print("  S -> ε")
print("  A -> S tres B C")
print("  A -> cuatro")
print("  A -> ε")
print("  B -> A cinco C seis")
print("  B -> ε")
print("  C -> siete B")
print("  C -> ε\n")

# conjuntos primeros
print("=" * 60)
print("PRIMEROS")
print("=" * 60)
PRIMEROS = {
    'S': {'dos', 'cuatro', 'cinco', 'siete', 'uno', 'ε'},
    'A': {'dos', 'cuatro', 'cinco', 'siete', 'uno', 'ε'},
    'B': {'dos', 'cuatro', 'cinco', 'siete', 'uno', 'ε'},
    'C': {'siete', 'ε'},
}
for nt, pr in PRIMEROS.items():
    print(f"  PRIMEROS({nt}) = {{ {', '.join(sorted(pr))} }}")
print()

# conjuntos siguientes
print("=" * 60)
print("SIGUIENTES")
print("=" * 60)
SIGUIENTES = {
    'S': {'$', 'tres'},
    'A': {'cinco'},
    'B': {'uno', 'seis', 'cinco'},
    'C': {'$', 'tres', 'seis'},
}
for nt, sg in SIGUIENTES.items():
    print(f"  SIGUIENTES({nt}) = {{ {', '.join(sorted(sg))} }}")
print()

# conjuntos de predicción
print("=" * 60)
print("PREDICCIÓN")
print("=" * 60)
PREDICCION = {
    'S -> B uno'      : {'dos', 'cuatro', 'cinco', 'siete', 'uno'},
    'S -> dos C'      : {'dos'},
    'S -> ε'          : {'$', 'tres'},
    'A -> S tres B C' : {'dos', 'cuatro', 'cinco', 'siete', 'uno', '$', 'tres'},
    'A -> cuatro'     : {'cuatro'},
    'A -> ε'          : {'cinco'},
    'B -> A cinco C seis': {'dos', 'cuatro', 'cinco', 'siete', 'uno', '$', 'tres'},
    'B -> ε'          : {'uno', 'seis', 'cinco'},
    'C -> siete B'    : {'siete'},
    'C -> ε'          : {'$', 'tres', 'seis'},
}
for regla, pred in PREDICCION.items():
    print(f"  PRED({regla}) = {{ {', '.join(sorted(pred))} }}")
print()

# verificación ll(1)
print("=" * 60)
print("¿ES LL(1)?")
print("=" * 60)
print("no, hay conflictos en S, A y B\n")

# parser descendente
_depth = 0

def parse_S():
    global _depth
    la = lookahead()
    _depth += 1
    # evita recursión infinita
    if _depth > 50:
        _depth -= 1
        return
    if la == 'dos':
        consume('dos')
        parse_C()
    elif la in ('$', 'tres'):
        pass  # ε
    else:
        parse_B()
        consume('uno')
    _depth -= 1

def parse_A():
    global _depth
    la = lookahead()
    _depth += 1
    if _depth > 50:
        _depth -= 1
        return
    if la == 'cuatro':
        consume('cuatro')
    elif la in ('cinco',):
        pass  # ε
    else:
        parse_S()
        consume('tres')
        parse_B()
        parse_C()
    _depth -= 1

def parse_B():
    global _depth
    la = lookahead()
    _depth += 1
    if _depth > 50:
        _depth -= 1
        return
    if la in ('uno', 'seis', 'cinco'):
        pass  # ε
    else:
        parse_A()
        consume('cinco')
        parse_C()
        consume('seis')
    _depth -= 1

def parse_C():
    # C -> siete B | ε
    if lookahead() == 'siete':
        consume('siete')
        parse_B()

# pruebas
print("=" * 60)
print("ASDR")
print("=" * 60)

ejemplos = [
    "dos siete",
    "cuatro cinco seis uno",
    "",
    "dos",
]

for ejemplo in ejemplos:
    desc = f"'{ejemplo}'" if ejemplo else "'(vacía)'"
    print(f"Cadena: {desc}")
    tokenize(ejemplo if ejemplo else "")
    _depth = 0
    try:
        parse_S()
        if lookahead() == '$':
            print("  → ACEPTADA ✓\n")
        else:
            print(f"  → RECHAZADA (sobran tokens desde '{lookahead()}') ✗\n")
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
    _depth = 0
    try:
        parse_S()
        if lookahead() == '$':
            print("  → ACEPTADA ✓\n")
        else:
            print(f"  → RECHAZADA '{lookahead()}' ✗\n")
    except SystemExit:
        print("  → RECHAZADA ✗\n")
