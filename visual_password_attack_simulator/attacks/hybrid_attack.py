"""
Implementación de un ataque híbrido (diccionario + sufijo numérico).

El ataque híbrido combina un diccionario base con sufijos numéricos para
aproximarse a contraseñas compuestas por palabras comunes seguidas de
números (por ejemplo, "contraseña123").  Se usa una lista de palabras
base y para cada una se generan sufijos desde 0 hasta un máximo
configurable.  Cada combinación se compara con el hash objetivo.
"""

import random
import re
import time
from pathlib import Path
from typing import Iterable, Optional, Sequence

from .base_attack import AttackThread
from ..utils.hash_utils import sha256_hash
from ..utils.password_requirements import (
    ALLOWED_SPECIAL_CHARACTERS,
    PASSWORD_LENGTH,
    meets_password_requirements,
)

MAX_BASE_LENGTH = PASSWORD_LENGTH
NON_ALNUM_RE = re.compile(r'[^A-Za-z0-9]')
YEARS = [str(y) for y in range(2000, 2027)]
LEET_MAP = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "$"}
DIGITS = "0123456789"
SPECIALS_PRIORITY: Sequence[str] = tuple(ch for ch in "*.-_@=+#$%&." if ch in ALLOWED_SPECIAL_CHARACTERS)


class HybridAttack(AttackThread):
    """Ataque híbrido: palabra de diccionario + sufijo numérico."""

    def __init__(self, target_hash: str, dictionary_path: Optional[str] = None, max_suffix: int = 999) -> None:
        super().__init__(target_hash)
        if dictionary_path is None:
            dictionary_path = Path(__file__).resolve().parent.parent / "hybrid_bases.txt"
        self.dictionary_path = Path(dictionary_path)
        self.max_suffix = max_suffix
        # El número total de candidatos depende de la combinación de variaciones,
        # números y símbolos; lo dejamos como desconocido (0) para el panel.
        self.total_candidates = 0

    def _sanitize_word(self, word: str) -> str:
        """Elimina caracteres no alfanuméricos y recorta a la longitud permitida."""
        cleaned = NON_ALNUM_RE.sub('', word.strip())
        return cleaned[:MAX_BASE_LENGTH]

    def _base_variants(self, cleaned: str) -> set[str]:
        """Genera variaciones básicas de mayúsculas/minúsculas para la palabra base."""
        if not cleaned:
            return set()
        lower = cleaned.lower()
        variants = {lower}
        if lower:
            variants.add(lower[0].upper() + lower[1:])
        if len(lower) > 1:
            variants.add(lower[:-1] + lower[-1].upper())
        variants.add(lower.swapcase())
        variants.add(self._apply_leet(lower))
        return {variant[:MAX_BASE_LENGTH] for variant in variants if variant}

    def _apply_leet(self, text: str) -> str:
        result = []
        for ch in text:
            repl = LEET_MAP.get(ch.lower())
            if repl and random.random() < 0.6:
                result.append(repl)
            else:
                result.append(ch)
        return "".join(result)

    def _weighted_special(self) -> str:
        if not SPECIALS_PRIORITY:
            return next(iter(ALLOWED_SPECIAL_CHARACTERS))
        weights = list(reversed(range(1, len(SPECIALS_PRIORITY) + 1)))
        return random.choices(SPECIALS_PRIORITY, weights=weights, k=1)[0]

    def _pattern_vader(self, root: str) -> str:
        if len(root) < 5:
            return ""
        root = self._apply_leet(root[:5])
        root = root[0].upper() + root[1:]
        year = random.choice(YEARS)
        sp = self._weighted_special()
        return root + year + sp

    def _pattern_luca(self, root: str) -> str:
        if len(root) < 4:
            return ""
        root = self._apply_leet(root[:4])
        root = root[0].upper() + root[1:]
        d = random.choice(DIGITS)
        sp = self._weighted_special()
        year = random.choice(YEARS)
        return root + d + sp + year

    def _pattern_fernando(self, root: str) -> str:
        if len(root) < 8:
            return ""
        root = self._apply_leet(root[:8])
        root = root[0].upper() + root[1:]
        d = random.choice(DIGITS)
        sp = self._weighted_special()
        return root + d + sp

    def _pattern_tail(self, root: str) -> str:
        if len(root) < 6:
            return ""
        root = self._apply_leet(root[:8])
        root = root[0].upper() + root[1:]
        d = random.choice(DIGITS)
        sp = self._weighted_special()
        return root + d + sp

    def _pattern_double_digit(self, root: str) -> str:
        if len(root) < 7:
            return ""
        root = self._apply_leet(root[:7])
        root = root[0].upper() + root[1:]
        d1 = random.choice(DIGITS)
        d2 = random.choice(DIGITS)
        sp = self._weighted_special()
        return root + d1 + d2 + sp

    def _generate_candidates(self, base_word: str) -> Iterable[str]:
        """Produce candidatos combinando la palabra base con patrones human-like."""
        cleaned = self._sanitize_word(base_word)
        variants = [variant for variant in self._base_variants(cleaned) if variant]
        if not variants:
            return
        patterns = (
            self._pattern_vader,
            self._pattern_luca,
            self._pattern_fernando,
            self._pattern_tail,
            self._pattern_double_digit,
        )
        seen: set[str] = set()
        for _ in range(max(1, self.max_suffix)):
            variant = random.choice(variants)
            pattern = random.choice(patterns)
            candidate = pattern(variant)
            if not candidate or len(candidate) != PASSWORD_LENGTH:
                continue
            if candidate in seen:
                continue
            if not meets_password_requirements(candidate):
                continue
            seen.add(candidate)
            yield candidate

    def run(self) -> None:
        self.start_time = time.time()
        attempts = 0
        try:
            with self.dictionary_path.open('r', encoding='utf-8', errors='ignore') as f:
                for base_word in f:
                    if not self.running:
                        self.log_message("Ataque h?brido cancelado por el usuario.")
                        self.finished.emit()
                        return
                    base_word = base_word.strip()
                    if not base_word:
                        continue
                    for candidate in self._generate_candidates(base_word):
                        if not self.running:
                            self.log_message("Ataque h?brido cancelado por el usuario.")
                            self.finished.emit()
                            return
                        attempts += 1
                        h = sha256_hash(candidate)
                        if h == self.target_hash:
                            elapsed = time.time() - self.start_time
                            self.found.emit(candidate, attempts, elapsed)
                            self.running = False
                            self.finished.emit()
                            return
                        elapsed = time.time() - self.start_time
                        self.progress.emit(attempts, self.total_candidates, elapsed)
                        if attempts % 500 == 0:
                            self.log_message(f"Probando: {candidate}")
        except FileNotFoundError:
            self.log_message(f"No se encontr? el diccionario: {self.dictionary_path}")
        elapsed = time.time() - self.start_time
        self.progress.emit(attempts, self.total_candidates, elapsed)
        self.log_message("Ataque h?brido finalizado sin ?xito.")
        self.finished.emit()
