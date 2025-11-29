"""
Implementación de un ataque por máscara de patrón.

El ataque de máscara permite al usuario definir un patrón de caracteres
especificando qué tipo de carácter va en cada posición.  Por ejemplo,
"?u?l?l?l?d?d" significa una cadena con una mayúscula, tres minúsculas y
dos dígitos.  Este módulo interpreta la máscara, genera todas las
combinaciones posibles dentro de ese patrón y compara sus hashes con el
objetivo.  Se trata de un ataque más eficiente que la fuerza bruta cuando
se conoce la estructura aproximada de la contraseña.
"""

import itertools
import time
from pathlib import Path
from typing import List, Optional

from .base_attack import AttackThread
from ..utils.hash_utils import sha256_hash
from ..utils.password_requirements import (
    ALLOWED_CHARACTERS,
    ALLOWED_SPECIAL_CHARACTERS,
    meets_password_requirements,
)


MASK_SETS = {
    'u': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'l': 'abcdefghijklmnopqrstuvwxyz',
    'd': '0123456789',
    's': ALLOWED_SPECIAL_CHARACTERS,
    'a': ALLOWED_CHARACTERS,
}


class MaskAttack(AttackThread):
    """Ataque de máscara de patrón."""

    def __init__(
        self,
        target_hash: str,
        mask: Optional[str] = None,
        mask_source: Optional[str] = None,
        use_custom: bool = False,
    ) -> None:
        super().__init__(target_hash)
        self.mask = mask
        self.mask_source = Path(mask_source) if mask_source else None
        self.use_custom = use_custom
        self.alphabets: List[str] = []
        self.total_candidates = 1
        self._load_mask()

    def _load_mask(self) -> None:
        mask_pattern = self.mask
        if self.mask_source and self.mask_source.exists():
            try:
                with self.mask_source.open('r', encoding='utf-8', errors='ignore') as f:
                    base = f.readline().strip()
                    if base:
                        mask_pattern = self._mask_from_base(base)
            except FileNotFoundError:
                self.log_message(f"No se encontró la máscara personalizada: {self.mask_source}")
        if not mask_pattern:
            mask_pattern = '?u?l?l?l?d?d'
        self._parse_mask(mask_pattern)

    def _mask_from_base(self, base: str) -> str:
        """Crea una máscara aproximada a partir de una base."""
        filtered = ''.join(ch for ch in base if ch in ALLOWED_CHARACTERS)
        if not filtered:
            return '?u?l?l?l?d?d'
        mask_parts: List[str] = []
        for ch in filtered[:10]:
            if ch.isupper():
                mask_parts.append('?u')
            elif ch.islower():
                mask_parts.append('?l')
            elif ch.isdigit():
                mask_parts.append('?d')
            else:
                mask_parts.append('?s')
        while len(mask_parts) < 10:
            mask_parts.append('?d')
        mask_str = ''.join(mask_parts)
        if '?s' not in mask_str:
            mask_str = mask_str[:-2] + '?s?d'
        return mask_str

    def _parse_mask(self, mask: str) -> None:
        self.alphabets.clear()
        self.total_candidates = 1
        i = 0
        while i < len(mask):
            if mask[i] == '?':
                i += 1
                if i < len(mask):
                    code = mask[i]
                    chars = MASK_SETS.get(code, '')
                    self.alphabets.append(chars)
                    self.total_candidates *= max(1, len(chars))
                else:
                    break
            else:
                self.alphabets.append(mask[i])
                self.total_candidates *= 1
            i += 1

    def run(self) -> None:
        self.start_time = time.time()
        attempts = 0
        # Generar combinaciones de acuerdo con la máscara
        for combo in itertools.product(*self.alphabets):
            if not self.running:
                self.log_message("Ataque de máscara cancelado por el usuario.")
                self.finished.emit()
                return
            candidate = ''.join(combo)
            if not meets_password_requirements(candidate):
                continue
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
        # Finalizar sin éxito
        elapsed = time.time() - self.start_time
        self.progress.emit(attempts, self.total_candidates, elapsed)
        self.log_message("Ataque de máscara finalizado sin éxito.")
        self.finished.emit()
