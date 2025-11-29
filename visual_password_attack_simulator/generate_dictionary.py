#!/usr/bin/env python3
"""
generate_dictionary_with_keywords.py

Genera un diccionario de contraseñas de prueba para el simulador,
a partir de:

1) Palabras clave típicas de estudiantes
   (Ibero, carreras, hobbies, equipos de futbol, etc.).
2) Contraseñas comunes en español (bases), adaptadas
   para cumplir las reglas de longitud y complejidad.
3) Entradas de:
   - allwords.txt               (diccionario de palabras en español)
   - password-list-mx.txt       (contraseñas comunes en MX)
   - female_names.csv           (nombres femeninos, jvalhondo/spanish-names-surnames)
   - male_names.csv             (nombres masculinos)
   - surnames1.csv              (apellidos, equivalente a surnames_freq_*.csv)
   - surnames2.csv              (apellidos, equivalente a surnames_freq_*.csv)

Todas las entradas se usan como BASE para generar variantes que
CUMPLAN las reglas A–D, con patrones "human-like":

- Mayúscula en primera/última letra.
- Reemplazos leet comunes (o->0, e->3, s->$, etc.).
- Inclusión de años 2000-2026 (ej. Vader2025#, Luca1$2020).
- Últimos dos caracteres como dígito + especial en muchos casos
  (ej. fernando0.).

Además:
- Se incluyen tal cual (sin modificar) las palabras de EXACTAMENTE
  10 caracteres que ya cumplan las reglas.
- Se guardan también, en otro archivo, TODAS las palabras "viables"
  de MENOS de 10 caracteres (tal como aparecen en los archivos) para
  usarlas como diccionario base del ataque híbrido.

REGLAS DEL PROYECTO:
A. Debe contener exactamente 10 caracteres.
B. Debe estar formada por dígitos, letras ASCII y al menos
   UN carácter especial de este conjunto:
   * . - _ @ = | + < > % & # $
C. No debe contener Ñ, ñ ni vocales acentuadas (solo ASCII).
D. Debe incluir al menos una letra mayúscula y al menos una minúscula.

Uso educativo para la vitrina de clase en IberoCDMX.
NO usar ni reutilizar estas contraseñas en sistemas reales.
"""

import random
import string
import re
from pathlib import Path
from typing import Set, Tuple

# ==========================
# Parámetros de configuración
# ==========================

HERE = Path(__file__).resolve().parent
OUTPUT_FILE = HERE / "dictionary.txt"          # contraseñas finales (10 chars)
HYBRID_BASES_FILE = HERE / "hybrid_bases.txt"  # palabras <10 chars tal cual

# Ficheros externos (todos en el mismo directorio que este script)
ALLWORDS_FILE = HERE / "allwords.txt"
PASSWORD_MX_FILE = HERE / "password-list-mx.txt"
FEMALE_NAMES_FILE = HERE / "female_names.csv"
MALE_NAMES_FILE = HERE / "male_names.csv"
SURNAMES1_FILE = HERE / "surnames1.csv"
SURNAMES2_FILE = HERE / "surnames2.csv"

UPPER = string.ascii_uppercase          # A-Z
LOWER = string.ascii_lowercase          # a-z
DIGITS = string.digits                  # 0-9

# Conjunto completo permitido por la política (para validar):
# * . - _ @ = | + < > % & # $
SPECIALS_FULL = "*.-_@=|+<>%&#$"

# Para generación, usamos una prioridad de símbolos:
# * . - _ @ = + # $ % & .
# (No incluimos | < > en la prioridad, pero sí se aceptan al validar
# porque están en SPECIALS_FULL).
SPECIALS_PRIORITY = []
for ch in "*.-_@=+#$%&.":
    if ch not in SPECIALS_PRIORITY:
        SPECIALS_PRIORITY.append(ch)

SPECIALS = "".join(sorted(set(SPECIALS_FULL)))  # para el conjunto permitido

ALL_CHARS = UPPER + LOWER + DIGITS + SPECIALS

# Años que queremos usar en las contraseñas human-like
YEARS = [str(y) for y in range(2000, 2027)]

# Mapa leet básico para hacer sustituciones tipo humano
LEET_MAP = {
    "a": "4",
    "e": "3",
    "i": "1",
    "o": "0",
    "s": "$",
}


# ==========================
# Reglas de validación de contraseña final
# ==========================

def cumple_reglas(pwd: str) -> bool:
    """
    Verifica que la contraseña cumpla las reglas A-D.
    """
    # Regla A
    if len(pwd) != 10:
        return False

    # Regla C: no Ñ/ñ ni vocales acentuadas
    if any(ch in "ÑñáéíóúÁÉÍÓÚ" for ch in pwd):
        return False

    # Regla D: al menos una mayúscula y una minúscula
    if not any(ch in UPPER for ch in pwd):
        return False
    if not any(ch in LOWER for ch in pwd):
        return False

    # Regla B: al menos un carácter especial del conjunto permitido
    if not any(ch in SPECIALS_FULL for ch in pwd):
        return False

    # Regla B (alfabeto permitido)
    if any(ch not in ALL_CHARS for ch in pwd):
        return False

    return True


# ==========================
# 1. Keywords de estudiantes / Ibero
# ==========================

STUDENT_KEYWORDS = [
    # clase
    "fernanda", "amezquita", "gordillo", "andres", "assam", "santiago", "angel", "isacc", "cabrera", "leal", "fernanda", "canales", "martinez", "ana", "karen", "cerisola", "ludskanov", "alejandro", "gabriel", "gonzalez", "assaf", "ely", "johana", "ibarra", "contreras", "fernando", "juarez", "medrano", "alessio", "luiselli", "majul", "yael", "roman", "maya", "diaz", "atom", "alexander", "muñoz", "nava", "harold", "david", "perez", "garcia", "omar", "vazquez", "gonzalez",
    # Ibero / universidad
    "ibero", "uiberomx", "lobos", "laboratorio", "ingenieria",
    "telecom", "robotica", "programacion", "electronica", "mecatronica",
    "computo", "fisica", "mate", "seguridad", "hack", "redes",

    # Materias y temas típicos
    "python", "ciberseguridad", "criptografia", "arduino", "raspberry",
    "stm32", "esp32", "iot", "matlab", "linux", "windows",

    # Vida estudiantil / hobbies
    "netflix", "spotify", "gamer", "futbol", "musica", "guitarra",
    "anime", "kpop", "cafe", "tacos", "birria", "pozole",

    # Equipos de futbol (sin acentos)
    "america", "chivas", "pumas", "cruzazul", "barcelona", "realMadrid",
    "tigres", "rayados"
]

# ==========================
# 2. Contraseñas comunes en español (bases)
# ==========================

COMMON_SPANISH_PASSWORDS = [
    "123456", "123456789", "1234567890",
    "qwerty", "qwertyui", "asdfgh",
    "teamo", "amormio", "miamor",
    "mexico", "vivaMexico", "miPerro",
    "miGato", "novio", "novia",
    "familia", "amigos", "password",
    "contrasena",  # en lugar de "contraseña"
]


# ==========================
# Helpers de transformación
# ==========================

def limpiar_base(base: str) -> str:
    """
    Limpia una palabra base:
    - Minúsculas
    - Solo letras y dígitos (otros caracteres se eliminan)
    - Sin ñ ni acentos (si aparecen, se descarta)
    """
    base = base.strip()
    base = base.replace(" ", "")  # quitamos espacios
    base = base.lower()
    # filtra a [a-z0-9]
    base = re.sub(r"[^a-z0-9]", "", base)
    # descartamos si quedan ñ/acentos por alguna razón (defensivo)
    if any(ch in "ñáéíóú" for ch in base):
        return ""
    return base


def aplicar_leet_simple(s: str) -> str:
    """
    Aplica sustituciones leet comunes de forma probabilística:
    a -> 4, e -> 3, i -> 1, o -> 0, s -> $
    No sustituye siempre, para que se vea más 'humano'.
    """
    res = []
    for ch in s:
        repl = LEET_MAP.get(ch)
        # ~60% de probabilidad de sustituir cuando hay mapeo
        if repl and random.random() < 0.6:
            res.append(repl)
        else:
            res.append(ch)
    return "".join(res)


def elegir_special_prioritario() -> str:
    """
    Elige un carácter especial ponderando más los que están antes
    en SPECIALS_PRIORITY.
    """
    n = len(SPECIALS_PRIORITY)
    weights = [n - i for i in range(n)]
    return random.choices(SPECIALS_PRIORITY, weights=weights, k=1)[0]


# ==========================
# Generación de variantes "human-like"
# ==========================

def generar_variantes_desde_base(base: str, max_variantes: int = 10) -> Set[str]:
    """
    Genera variantes 'human-like' de una palabra base, siguiendo
    patrones típicos de usuarios:

    - Mayúscula en primera/última letra.
    - Reemplazos leet comunes (o->0, e->3, s->$, etc.).
    - Inclusión de años 2000-2026 (p.ej. 2020, 2024, 2025).
    - Últimos dos caracteres como dígito + especial en muchos casos
      (ej. 'fernando0.', 'Luca1$2025').

    Debe intentar generar AL MENOS 5 variaciones por base "viable".
    Si la base es muy larga, se trunca para usarla.
    """

    variantes: Set[str] = set()
    base_clean = limpiar_base(base)
    if not base_clean:
        return variantes

    # Truncamos bases absurdamente largas
    if len(base_clean) > 10:
        base_clean = base_clean[:10]

    # Aseguramos que max_variantes sea al menos 5
    max_variantes = max(max_variantes, 5)

    # Construimos raíces 'humanas': normal, capitalizada, leet, etc.
    roots: Set[str] = set()

    # raíz tal cual (minúsculas)
    roots.add(base_clean)

    # capitalizar primera letra
    if len(base_clean) >= 1:
        roots.add(base_clean[0].upper() + base_clean[1:])

    # capitalizar última letra
    if len(base_clean) >= 1:
        roots.add(base_clean[:-1] + base_clean[-1].upper())

    # versión leet simple
    roots.add(aplicar_leet_simple(base_clean))

    # versión leet + mayúscula inicial
    if len(base_clean) >= 1:
        leet_cap = aplicar_leet_simple(base_clean[0].upper() + base_clean[1:])
        roots.add(leet_cap)

    roots = [r for r in roots if r]
    if not roots:
        return variantes

    digits = DIGITS

    def pattern_vader(root: str) -> str:
        """
        Estilo: Vader2025#
        base(5) + año(4) + special(1) = 10
        """
        if len(root) < 5:
            return ""
        r = root[:5]
        r = r[0].upper() + r[1:]
        year = random.choice(YEARS)
        sp = elegir_special_prioritario()
        return r + year + sp  # 5 + 4 + 1 = 10

    def pattern_luca(root: str) -> str:
        """
        Estilo: Luca1$2025
        base(4) + dígito(1) + special(1) + año(4) = 10
        """
        if len(root) < 4:
            return ""
        r = root[:4]
        r = r[0].upper() + r[1:]
        d = random.choice(digits)
        sp = elegir_special_prioritario()
        year = random.choice(YEARS)
        return r + d + sp + year  # 4 + 1 + 1 + 4 = 10

    def pattern_fernando(root: str) -> str:
        """
        Estilo: fernando0.
        base(8) + dígito + special = 10
        Últimos dos caracteres: número + especial.
        """
        if len(root) < 8:
            return ""
        r = aplicar_leet_simple(root[:8])
        # mezclamos may/min: mayúscula inicial para asegurar una
        r = r[0].upper() + r[1:]
        d = random.choice(digits)
        sp = elegir_special_prioritario()
        return r + d + sp  # 8 + 1 + 1 = 10

    def pattern_caballo(root: str) -> str:
        """
        Estilo: C4b4llo12$
        base(7 leet) + dígito + dígito + special = 10
        """
        if len(root) < 7:
            return ""
        r = aplicar_leet_simple(root[:7])
        r = r[0].upper() + r[1:]
        d1 = random.choice(digits)
        d2 = random.choice(digits)
        sp = elegir_special_prioritario()
        return r + d1 + d2 + sp  # 7 + 1 + 1 + 1 = 10

    def pattern_tail_digits_special(root: str) -> str:
        """
        Variante genérica: base(8 leet/cap) + dígito + special = 10
        Similar a 'fernando0.' pero para bases que al menos tengan 6 chars.
        """
        if len(root) < 6:
            return ""
        # Queremos 8 chars de raíz
        r = root
        if len(r) > 8:
            r = r[:8]
        r = aplicar_leet_simple(r)
        # aseguramos al menos una mayúscula
        r = r[0].upper() + r[1:]
        d = random.choice(digits)
        sp = elegir_special_prioritario()
        return r + d + sp  # 8 + 1 + 1 = 10

    patrones = [
        pattern_vader,
        pattern_luca,
        pattern_fernando,
        pattern_caballo,
        pattern_tail_digits_special,
    ]

    intentos = 0
    max_intentos = max_variantes * 60  # margen amplio

    while len(variantes) < max_variantes and intentos < max_intentos:
        intentos += 1
        root = random.choice(roots)
        patron = random.choice(patrones)
        cand = patron(root)

        if not cand:
            continue
        if len(cand) != 10:
            continue
        if not cumple_reglas(cand):
            continue

        variantes.add(cand)

    return variantes


# ==========================
# Helpers para bases híbridas
# ==========================

def raw_viable_for_hybrid(raw: str) -> bool:
    """
    Determina si una palabra tal cual podría ser útil como base
    para el ataque híbrido:
    - Longitud entre 3 y 9 (menor que 10).
    - Sin espacios.
    - Sin ñ ni vocales acentuadas (para simplificar).
    """
    if not (3 <= len(raw) < 10):
        return False
    if any(ch.isspace() for ch in raw):
        return False
    if any(ch in "ÑñáéíóúÁÉÍÓÚ" for ch in raw):
        return False
    return True


# ==========================
# Carga de bases externas
# ==========================

def cargar_bases_externas() -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Carga palabras base desde:
    - allwords.txt
    - password-list-mx.txt
    - female_names.csv
    - male_names.csv
    - surnames1.csv
    - surnames2.csv

    Devuelve:
      - bases: palabras base limpias (para generar variaciones)
      - originales10: palabras EXACTAMENTE de 10 caracteres que,
        tal cual están escritas, ya cumplen las reglas y se incluirán
        directamente en el diccionario final.
      - hybrid_bases_raw: palabras <10 chars "tal cual" (como en archivo),
        filtradas, para usarlas como diccionario base en el ataque híbrido.
    """
    bases: Set[str] = set()
    originales10: Set[str] = set()
    hybrid_bases_raw: Set[str] = set()

    paths = [
        ALLWORDS_FILE,
        PASSWORD_MX_FILE,
        FEMALE_NAMES_FILE,
        MALE_NAMES_FILE,
        SURNAMES1_FILE,
        SURNAMES2_FILE,
    ]

    for path in paths:
        if not path.exists():
            print(f"[WARN] Wordlist externo no encontrado: {path}")
            continue

        print(f"[INFO] Cargando wordlist externo: {path.name}")
        count_lines = 0
        is_csv = path.suffix.lower() == ".csv"

        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                count_lines += 1

                raw_items = []

                if is_csv:
                    # Tomamos la primera columna
                    first_field = line.split(",")[0].strip().strip('"')
                    if not first_field:
                        continue
                    lf = first_field.lower()
                    # Saltamos cabeceras típicas
                    if lf in ("name", "surname"):
                        continue

                    # Para nombres, dividimos nombres compuestos ("MARIA CARMEN")
                    if "female" in path.name.lower() or "male" in path.name.lower():
                        tokens = [t.strip() for t in first_field.split() if t.strip()]
                        raw_items.extend(tokens)
                    else:
                        # Para apellidos usamos el campo completo
                        raw_items.append(first_field)
                else:
                    # TXT plano: usamos la línea completa como raw
                    raw_items.append(line)

                for raw in raw_items:
                    # Incluir "tal cual" si ya tiene 10 caracteres y cumple las reglas
                    if len(raw) == 10 and cumple_reglas(raw):
                        originales10.add(raw)

                    # Guardar palabra "tal cual" para hybrid si < 10 caracteres y viable
                    if raw_viable_for_hybrid(raw):
                        hybrid_bases_raw.add(raw)

                    # Limpiar para usar como base (minúsculas, [a-z0-9])
                    w = limpiar_base(raw)
                    if not w:
                        continue

                    # Si la palabra es demasiado larga, la truncamos como base
                    if len(w) > 10:
                        w = w[:10]

                    # Longitud mínima razonable para base
                    if len(w) >= 3:
                        bases.add(w)

                if count_lines % 100000 == 0:
                    print(f"[INFO] Leídas {count_lines} líneas de {path.name}...")

        print(f"[INFO] Total de líneas leídas de {path.name}: {count_lines}")

    print(f"[INFO] Total de bases externas cargadas (limpias): {len(bases)}")
    print(f"[INFO] Total de palabras de 10 caracteres válidas tal cual: {len(originales10)}")
    print(f"[INFO] Total de palabras <10 chars guardadas para hybrid: {len(hybrid_bases_raw)}")
    return bases, originales10, hybrid_bases_raw


def generar_contraseñas_desde_bases() -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Genera contraseñas a partir de:

    - STUDENT_KEYWORDS
    - COMMON_SPANISH_PASSWORDS
    - Palabras provenientes de allwords/password-list-mx
    - Nombres y apellidos de female_names.csv, male_names.csv,
      surnames1.csv, surnames2.csv

    Todas las contraseñas generadas (variantes) deben cumplir las reglas.
    NO se generan contraseñas completamente aleatorias.

    Devuelve:
      - variantes: contraseñas generadas por reglas (10 chars)
      - originales10: palabras incluidas "tal cual" (10 chars válidos)
      - hybrid_bases_all: conjunto de palabras <10 chars "tal cual"
        para usar en el ataque híbrido (incluye externas e internas).
    """
    # bases internas (keywords y contraseñas comunes)
    bases_internas = set(STUDENT_KEYWORDS) | set(COMMON_SPANISH_PASSWORDS)

    # bases externas + originales de 10 chars válidas + palabras <10 para hybrid
    bases_externas, originales10, hybrid_bases_raw = cargar_bases_externas()

    # También queremos incluir las internas como posibles bases "tal cual"
    # para hybrid, siempre que cumplan la longitud y filtro de hybrid.
    for w in (STUDENT_KEYWORDS + COMMON_SPANISH_PASSWORDS):
        if raw_viable_for_hybrid(w):
            hybrid_bases_raw.add(w)

    # Todas las bases limpias para variaciones
    bases = bases_internas | bases_externas
    total_bases = len(bases)
    print(f"[INFO] Generando variantes a partir de {total_bases} bases limpias...")

    variantes: Set[str] = set()

    for idx, base in enumerate(bases, start=1):
        # Al menos 5 variaciones por base viable.
        # Más variaciones para bases internas (palabras clave del contexto Ibero).
        if base in bases_internas:
            max_var = 2000
        else:
            max_var = 10

        nuevas = generar_variantes_desde_base(base, max_variantes=max_var)
        variantes.update(nuevas)

        # Progreso en "tiempo real" (cada cierto número de bases)
        if idx % 500 == 0 or idx == total_bases:
            print(
                f"[INFO] Procesadas {idx}/{total_bases} bases; "
                f"contraseñas acumuladas (variantes): {len(variantes)}"
            )

    print(f"[INFO] Variantes totales generadas: {len(variantes)}")

    # hybrid_bases_all = todas las palabras <10 chars tal cual
    hybrid_bases_all: Set[str] = set(hybrid_bases_raw)

    print(f"[INFO] Total de bases 'tal cual' para hybrid (internas + externas): {len(hybrid_bases_all)}")
    return variantes, originales10, hybrid_bases_all


# ==========================
# MAIN
# ==========================

def main():
    random.seed()  # se puede fijar semilla para reproducibilidad si se desea

    print("[INFO] Iniciando generación de diccionario...")
    variantes, originales10, hybrid_bases = generar_contraseñas_desde_bases()

    # Diccionario final = originales válidos de 10 chars + todas las variantes generadas
    dict_final: Set[str] = set(originales10)
    dict_final.update(variantes)

    print(f"[INFO] Total de contraseñas antes de deduplicar: {len(originales10) + len(variantes)}")
    print(f"[INFO] Total de contraseñas únicas en el diccionario final: {len(dict_final)}")

    # Guardar contraseñas finales (10 chars, cumpliendo reglas)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for pwd in sorted(dict_final):
            f.write(pwd + "\n")

    print(f"[OK] Diccionario (10 chars) generado en: {OUTPUT_FILE.resolve()}")
    print(f"[OK] Total de contraseñas escritas: {len(dict_final)}")

    # Guardar bases para ataque híbrido (palabras <10 chars tal cual)
    with HYBRID_BASES_FILE.open("w", encoding="utf-8") as f:
        for w in sorted(hybrid_bases):
            f.write(w + "\n")

    print(f"[OK] Bases para ataque híbrido generadas en: {HYBRID_BASES_FILE.resolve()}")
    print(f"[OK] Total de palabras base para hybrid: {len(hybrid_bases)}")


if __name__ == "__main__":
    main()
