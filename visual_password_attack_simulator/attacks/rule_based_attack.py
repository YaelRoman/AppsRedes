"""
Implementación de un ataque basado en reglas de transformación.

Este ataque aplica un conjunto de reglas de manipulación (mangling) a
palabras de un diccionario para generar variantes que los usuarios a
menudo emplean, como poner la primera letra en mayúsculas, sustituir
letras por números o añadir sufijos comunes.  Las transformaciones se
aplican individualmente o en combinación limitada para evitar un número
explosivo de candidatos.  Cada variante se compara con el hash de la
contraseña objetivo.
"""

import time
from pathlib import Path
from typing import List, Optional

from .base_attack import AttackThread
from ..utils.hash_utils import sha256_hash
from ..utils.password_requirements import meets_password_requirements


class RuleBasedAttack(AttackThread):
    """Ataque basado en reglas de mangling."""

    def __init__(self, target_hash: str, dictionary_path: Optional[str] = None) -> None:
        super().__init__(target_hash)
        if dictionary_path is None:
            dictionary_path = Path(__file__).resolve().parent.parent / "dictionary.txt"
        self.dictionary_path = Path(dictionary_path)
        # No podemos estimar fácilmente el total ya que depende de las reglas
        self.total_candidates = 0

    def apply_rules(self, word: str) -> List[str]:
        """Genera variantes de una palabra aplicando reglas sencillas.

        La lista contiene la palabra original y las variantes.
        """
        variants = set()
        variants.add(word)
        # Regla: primera letra en mayúsculas
        if word:
            variants.add(word[0].upper() + word[1:])
        # Regla: última letra en mayúsculas
        if len(word) > 1:
            variants.add(word[:-1] + word[-1].upper())
        # Regla: sustitución de caracteres por números/símbolos
        substitutions = {
            'a': '@', 'A': '@',
            'e': '3', 'E': '3',
            'i': '1', 'I': '1',
            'o': '0', 'O': '0',
            's': '5', 'S': '5',
            'l': '1', 'L': '1',
        }
        for ch, repl in substitutions.items():
            if ch in word:
                variants.add(word.replace(ch, repl))
        # Regla: añadir sufijos
        suffixes = ['123', '!', '!23', '2024']
        for suf in suffixes:
            variants.add(word + suf)
        # Devolver como lista única
        return list(variants)

    def run(self) -> None:
        self.start_time = time.time()
        attempts = 0
        try:
            with self.dictionary_path.open('r', encoding='utf-8', errors='ignore') as f:
                for base_word in f:
                    if not self.running:
                        self.log_message("Ataque por reglas cancelado por el usuario.")
                        self.finished.emit()
                        return
                    base_word = base_word.strip()
                    if not base_word:
                        continue
                    variants = self.apply_rules(base_word)
                    for cand in variants:
                        if not self.running:
                            self.log_message("Ataque por reglas cancelado por el usuario.")
                            self.finished.emit()
                            return
                        if not meets_password_requirements(cand):
                            continue
                        attempts += 1
                        h = sha256_hash(cand)
                        if h == self.target_hash:
                            elapsed = time.time() - self.start_time
                            self.found.emit(cand, attempts, elapsed)
                            self.running = False
                            self.finished.emit()
                            return
                        elapsed = time.time() - self.start_time
                        # total_candidates permanece 0 ya que es indeterminado
                        self.progress.emit(attempts, 0, elapsed)
                        if attempts % 500 == 0:
                            self.log_message(f"Probando: {cand}")
        except FileNotFoundError:
            self.log_message(f"No se encontró el diccionario: {self.dictionary_path}")
        # Finalizar
        elapsed = time.time() - self.start_time
        self.progress.emit(attempts, 0, elapsed)
        self.log_message("Ataque por reglas finalizado sin éxito.")
        self.finished.emit()
