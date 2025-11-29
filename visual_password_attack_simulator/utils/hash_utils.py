"""
Funciones utilitarias para el cálculo de hashes y la evaluación de la entropía
de contraseñas.  Este módulo proporciona funciones para generar el hash SHA‑256
de una cadena y para estimar la entropía de una contraseña basada en su
longitud y el conjunto de caracteres utilizados.  La entropía se calcula
utilizando la fórmula log₂(N^L), donde N es el tamaño del alfabeto posible y
L es la longitud de la contraseña【671562893711359†L63-L69】.  Este cálculo
proporciona una aproximación de los bits de entropía, que puede
interpretarse como el número de intentos que un atacante tendría que
realizar de media para adivinar la contraseña en un ataque de fuerza bruta.

Además se incluyen funciones para clasificar la fortaleza de la contraseña
basándose en umbrales de entropía.  Según los ejemplos publicados, una
contraseña de ocho caracteres en minúsculas tiene aproximadamente 38 bits
de entropía, mientras que una contraseña de 12 caracteres usando mayúsculas,
minúsculas, números y símbolos puede superar los 79 bits【325584728368036†L420-L427】.
Generalmente se considera que una contraseña con más de 60 bits de entropía es
«muy fuerte»【325584728368036†L420-L427】.  Estas referencias sirven de guía
educativa, no como garantía de seguridad.
"""

import math
import hashlib
import string
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class PasswordAnalysis:
    """Representa los datos resultantes del análisis de una contraseña."""
    password: str
    length: int
    charsets: Dict[str, bool]
    entropy_bits: float
    strength_category: str
    suggestions: List[str]


def sha256_hash(text: str) -> str:
    """Devuelve el hash SHA‑256 de la cadena indicada.

    Args:
        text: Texto a codificar.

    Returns:
        Cadena hexadecimal con el hash SHA‑256.
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def calculate_entropy_bits(password: str) -> Tuple[float, int]:
    """Calcula la entropía aproximada de una contraseña en bits.

    Esta función estima los bits de entropía utilizando la fórmula
    log2(N^L)【671562893711359†L63-L69】, donde N es el número de caracteres
    posibles y L es la longitud de la contraseña.  Para la estimación de N
    se suman los tamaños de los subconjuntos de caracteres presentes en la
    contraseña: minúsculas (26), mayúsculas (26), dígitos (10) y símbolos
    (los caracteres imprimibles restantes).  Esta aproximación supone que
    cada carácter de la contraseña se elige de manera uniforme de entre los
    subconjuntos usados, por lo que la entropía real de contraseñas
    humanamente seleccionadas puede ser sensiblemente inferior.

    Args:
        password: Contraseña a analizar.

    Returns:
        Una tupla con los bits de entropía aproximados y la
        cardinalidad total del alfabeto utilizado.
    """
    # Definir subconjuntos de caracteres
    lowers = set(string.ascii_lowercase)
    uppers = set(string.ascii_uppercase)
    digits = set(string.digits)
    symbols = set(string.punctuation)
    used_sets = {
        'lower': any(ch in lowers for ch in password),
        'upper': any(ch in uppers for ch in password),
        'digit': any(ch in digits for ch in password),
        'symbol': any(ch in symbols for ch in password),
    }
    # Calcular N sumando los tamaños de los subconjuntos presentes
    N = 0
    if used_sets['lower']:
        N += len(lowers)
    if used_sets['upper']:
        N += len(uppers)
    if used_sets['digit']:
        N += len(digits)
    if used_sets['symbol']:
        N += len(symbols)
    L = len(password)
    if L == 0 or N == 0:
        return 0.0, N
    # Entropía en bits
    entropy = L * math.log2(N)
    return entropy, N


def classify_entropy(entropy_bits: float) -> str:
    """Clasifica la fortaleza de la contraseña según su entropía.

    Se utilizan umbrales aproximados basados en ejemplos de entropía: una
    contraseña con ~38 bits de entropía se considera débil y una con
    ~79 bits es muy fuerte【325584728368036†L420-L427】.  Los límites se han
    escalado gradualmente para ofrecer categorías intuitivas:

    - < 20 bits: Muy débil
    - 20–40 bits: Débil
    - 40–60 bits: Media
    - 60–80 bits: Fuerte
    - >= 80 bits: Muy fuerte

    Args:
        entropy_bits: Bits de entropía estimados.

    Returns:
        Cadena indicando la categoría.
    """
    if entropy_bits < 20:
        return "Muy débil"
    elif entropy_bits < 40:
        return "Débil"
    elif entropy_bits < 60:
        return "Media"
    elif entropy_bits < 80:
        return "Fuerte"
    else:
        return "Muy fuerte"


def analyze_password(password: str) -> PasswordAnalysis:
    """Analiza una contraseña y proporciona métricas básicas.

    Args:
        password: Contraseña a analizar.

    Returns:
        Objeto PasswordAnalysis con los resultados del análisis.
    """
    length = len(password)
    entropy_bits, N = calculate_entropy_bits(password)
    charsets = {
        'minúsculas': any(ch.islower() for ch in password),
        'mayúsculas': any(ch.isupper() for ch in password),
        'dígitos': any(ch.isdigit() for ch in password),
        'símbolos': any(ch in string.punctuation for ch in password),
    }
    category = classify_entropy(entropy_bits)
    suggestions: List[str] = []
    # Sugerencias simples para mejorar la contraseña
    if length < 8:
        suggestions.append("Utiliza al menos 8 caracteres.")
    if not charsets['minúsculas']:
        suggestions.append("Añade letras minúsculas.")
    if not charsets['mayúsculas']:
        suggestions.append("Añade letras mayúsculas.")
    if not charsets['dígitos']:
        suggestions.append("Incluye dígitos (0–9).")
    if not charsets['símbolos']:
        suggestions.append("Agrega símbolos o signos de puntuación.")
    if entropy_bits > 80:
        suggestions.append("Tu contraseña es muy fuerte; recuerda utilizar un gestor de contraseñas.")
    return PasswordAnalysis(
        password=password,
        length=length,
        charsets=charsets,
        entropy_bits=entropy_bits,
        strength_category=category,
        suggestions=suggestions,
    )