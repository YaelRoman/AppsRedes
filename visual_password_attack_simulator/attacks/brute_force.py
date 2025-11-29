"""
Implementación de un ataque de fuerza bruta.

Este módulo proporciona la clase `BruteForceAttack` que hereda de
``AttackThread``.  Genera sistemáticamente todas las combinaciones de un
alfabeto limitado hasta una longitud máxima especificada.  A cada
combinación se le aplica la función de hash SHA‑256 y se compara con el
hash objetivo.  Para mantener la demo receptiva, el tamaño del alfabeto y
la longitud máxima se establecen de forma conservadora.  Cada pocas
iteraciones se emiten señales de progreso y log.
"""

import itertools
import time
from typing import Optional

from .base_attack import AttackThread
from ..utils.hash_utils import sha256_hash
from ..utils.password_requirements import (
    ALLOWED_CHARACTERS,
    PASSWORD_LENGTH,
    meets_password_requirements,
)


class BruteForceAttack(AttackThread):
    """Ataque de fuerza bruta limitado por la política vigente."""

    def __init__(
        self,
        target_hash: str,
        alphabet: Optional[str] = None,
        max_length: Optional[int] = None,
        password_length: int = PASSWORD_LENGTH,
    ) -> None:
        """Inicializa el ataque de fuerza bruta adaptado a la política."""
        super().__init__(target_hash)
        raw_alphabet = alphabet or ALLOWED_CHARACTERS
        filtered = ''.join(ch for ch in raw_alphabet if ch in ALLOWED_CHARACTERS)
        self.alphabet = filtered or ALLOWED_CHARACTERS
        resolved_length = password_length or max_length or PASSWORD_LENGTH
        self.length = resolved_length
        self.total_candidates = len(self.alphabet) ** self.length

    def run(self) -> None:
        self.start_time = time.time()
        attempts = 0
        for combo in itertools.product(self.alphabet, repeat=self.length):
            if not self.running:
                self.log_message("Ataque de fuerza bruta cancelado por el usuario.")
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
        # Si se alcanza aquí, no se encontró la contraseña
        elapsed = time.time() - self.start_time
        self.progress.emit(attempts, self.total_candidates, elapsed)
        self.log_message("Fuerza bruta finalizada sin éxito.")
        self.finished.emit()
