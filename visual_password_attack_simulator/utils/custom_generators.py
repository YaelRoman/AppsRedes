"""
Generación de diccionarios personalizados a partir de palabras clave.

Este módulo implementa la lógica "human-like" descrita para crear
contraseñas de ejemplo y las bases del ataque híbrido. Se integra con
la interfaz para que el usuario pueda generar y activar estos archivos.
"""

from __future__ import annotations

import random
import re
import string
from pathlib import Path
from typing import Iterable, List, Sequence, Set, Tuple

from .password_requirements import (
    ALLOWED_SPECIAL_CHARACTERS,
    PASSWORD_LENGTH,
    meets_password_requirements,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
CUSTOM_DICTIONARY_PATH = ROOT_DIR / "custom_dictionary.txt"
CUSTOM_HYBRID_BASES_PATH = ROOT_DIR / "custom_hybrid_bases.txt"

TARGET_SIZE_DEFAULT = 30_000
YEARS = [str(y) for y in range(2000, 2027)]
LEET_MAP = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "$"}
SPECIALS_FULL = "".join(sorted(ALLOWED_SPECIAL_CHARACTERS))
SPECIALS_PRIORITY: Sequence[str] = tuple(ch for ch in "*.-_@=+#$%&." if ch in ALLOWED_SPECIAL_CHARACTERS)

UPPER = string.ascii_uppercase
LOWER = string.ascii_lowercase
DIGITS = string.digits
NON_ALNUM_RE = re.compile(r"[^a-z0-9]", re.IGNORECASE)


def _sanitize_keyword(keyword: str) -> str:
    """Mantiene caracteres alfanuméricos y descarta entradas vacías."""
    cleaned = "".join(ch for ch in keyword if ch.isalnum())
    return cleaned.lower()


def _clean_base(base: str) -> str:
    """Limpia la palabra base y elimina caracteres no permitidos."""
    candidate = NON_ALNUM_RE.sub("", base.strip().lower())
    if any(ch in "ñáéíóú" for ch in candidate):
        return ""
    return candidate


def _apply_leet(value: str) -> str:
    """Aplica sustituciones leet simples con una probabilidad del 60%."""
    result = []
    for ch in value:
        repl = LEET_MAP.get(ch.lower())
        if repl and random.random() < 0.6:
            result.append(repl)
        else:
            result.append(ch)
    return "".join(result)


def _weighted_special() -> str:
    """Elige un símbolo priorizando los primeros elementos."""
    if not SPECIALS_PRIORITY:
        return next(iter(ALLOWED_SPECIAL_CHARACTERS))
    weights = list(reversed(range(1, len(SPECIALS_PRIORITY) + 1)))
    return random.choices(SPECIALS_PRIORITY, weights=weights, k=1)[0]


def _base_variants(base_clean: str) -> List[str]:
    roots: Set[str] = set()
    roots.add(base_clean)
    if base_clean:
        roots.add(base_clean[0].upper() + base_clean[1:])
        roots.add(base_clean[:-1] + base_clean[-1].upper())
        roots.add(_apply_leet(base_clean))
        roots.add(_apply_leet(base_clean[0].upper() + base_clean[1:]))
    return [r for r in roots if r]


def generar_variantes_desde_base(base: str, max_variantes: int) -> Set[str]:
    variantes: Set[str] = set()
    base_clean = _clean_base(base)
    if not base_clean:
        return variantes
    if len(base_clean) > PASSWORD_LENGTH:
        base_clean = base_clean[:PASSWORD_LENGTH]
    roots = _base_variants(base_clean)
    if not roots:
        return variantes

    def pattern_vader(root: str) -> str:
        if len(root) < 5:
            return ""
        r = (root[:5])[0].upper() + (root[:5])[1:]
        year = random.choice(YEARS)
        sp = _weighted_special()
        return r + year + sp

    def pattern_luca(root: str) -> str:
        if len(root) < 4:
            return ""
        r = (root[:4])[0].upper() + (root[:4])[1:]
        d = random.choice(DIGITS)
        sp = _weighted_special()
        year = random.choice(YEARS)
        return r + d + sp + year

    def pattern_fernando(root: str) -> str:
        if len(root) < 8:
            return ""
        r = _apply_leet(root[:8])
        r = r[0].upper() + r[1:]
        d = random.choice(DIGITS)
        sp = _weighted_special()
        return r + d + sp

    def pattern_caballo(root: str) -> str:
        if len(root) < 7:
            return ""
        r = _apply_leet(root[:7])
        r = r[0].upper() + r[1:]
        d1 = random.choice(DIGITS)
        d2 = random.choice(DIGITS)
        sp = _weighted_special()
        return r + d1 + d2 + sp

    def pattern_tail(root: str) -> str:
        if len(root) < 6:
            return ""
        r = root[:8]
        r = _apply_leet(r)
        r = r[0].upper() + r[1:]
        d = random.choice(DIGITS)
        sp = _weighted_special()
        return r + d + sp

    patterns = (pattern_vader, pattern_luca, pattern_fernando, pattern_caballo, pattern_tail)

    attempts = 0
    max_attempts = max_variantes * 60
    while len(variantes) < max_variantes and attempts < max_attempts:
        attempts += 1
        root = random.choice(roots)
        candidate = random.choice(patterns)(root)
        if candidate and len(candidate) == PASSWORD_LENGTH and meets_password_requirements(candidate):
            variantes.add(candidate)
    return variantes


def generate_custom_dictionary(words: List[str], target_size: int = TARGET_SIZE_DEFAULT) -> Set[str]:
    """Genera contraseñas human-like a partir de la lista proporcionada."""
    base_words = [w for w in words if isinstance(w, str) and w.strip()]
    if not base_words:
        raise ValueError("Debes proporcionar al menos una palabra clave válida.")
    final_passwords: Set[str] = set()
    approx_per_word = max(5, target_size // len(base_words))
    for word in base_words:
        variants = generar_variantes_desde_base(word, max_variantes=approx_per_word)
        final_passwords.update(variants)
        if len(final_passwords) >= target_size:
            break
    if len(final_passwords) > target_size:
        final_passwords = set(random.sample(list(final_passwords), target_size))
    return final_passwords


def _generate_hybrid_bases(words: Iterable[str]) -> List[str]:
    bases: Set[str] = set()
    for word in words:
        cleaned = _clean_base(word)
        if not cleaned:
            continue
        bases.add(cleaned[: PASSWORD_LENGTH - 2] or "custom")
    if not bases:
        bases.add("custom")
    return sorted(bases)


def generate_custom_files(keywords: Iterable[str], target_size: int = TARGET_SIZE_DEFAULT) -> Tuple[Path, Path]:
    """Genera los archivos personalizados (diccionario e híbrido)."""
    cleaned_inputs = [_sanitize_keyword(word) for word in keywords if word.strip()]
    cleaned_inputs = [word for word in cleaned_inputs if word]
    if not cleaned_inputs:
        raise ValueError("Debes proporcionar al menos una palabra clave válida.")
    passwords = generate_custom_dictionary(cleaned_inputs, target_size)
    CUSTOM_DICTIONARY_PATH.write_text("\n".join(sorted(passwords)), encoding="utf-8")
    hybrid_bases = _generate_hybrid_bases(cleaned_inputs)
    CUSTOM_HYBRID_BASES_PATH.write_text("\n".join(hybrid_bases), encoding="utf-8")
    return CUSTOM_DICTIONARY_PATH, CUSTOM_HYBRID_BASES_PATH


__all__ = [
    "generate_custom_files",
    "generate_custom_dictionary",
    "CUSTOM_DICTIONARY_PATH",
    "CUSTOM_HYBRID_BASES_PATH",
]
