"""
Implementación de un ataque de diccionario.

Este ataque lee una lista de palabras comunes desde un archivo de texto y
compara el hash SHA‑256 de cada entrada con el hash objetivo.  Es una de
las técnicas más utilizadas debido a que muchos usuarios eligen
contraseñas que se encuentran en listas de contraseñas filtradas o
palabras del diccionario.  Para mantener la demo ágil, se emite
progreso después de cada entrada procesada y se permite cancelar la
ejecución en cualquier momento.
"""

import time
from pathlib import Path
from typing import Optional

from .base_attack import AttackThread
from ..utils.hash_utils import sha256_hash
from ..utils.password_requirements import meets_password_requirements

BATCH_SIZE = 1000


class DictionaryAttack(AttackThread):
    """Ataque basado en un diccionario de palabras."""

    def __init__(self, target_hash: str, dictionary_path: Optional[str] = None) -> None:
        super().__init__(target_hash)
        # Establecer ruta del diccionario; si no se proporciona se usa el
        # diccionario incluido en el paquete
        if dictionary_path is None:
            dictionary_path = Path(__file__).resolve().parent.parent / "dictionary.txt"
        self.dictionary_path = Path(dictionary_path)
        # Calcular total de entradas para progreso
        try:
            total = 0
            with self.dictionary_path.open('r', encoding='utf-8', errors='ignore') as f:
                while True:
                    batch = [line.strip() for _, line in zip(range(BATCH_SIZE), f)]
                    if not batch:
                        break
                    total += sum(1 for word in batch if meets_password_requirements(word))
            self.total_candidates = total
        except Exception:
            self.total_candidates = 0

    def run(self) -> None:
        self.start_time = time.time()
        attempts = 0
        try:
            with self.dictionary_path.open('r', encoding='utf-8', errors='ignore') as f:
                while True:
                    batch = [line.strip() for _, line in zip(range(BATCH_SIZE), f)]
                    if not batch:
                        break
                    for word in batch:
                        if not self.running:
                            self.log_message("Ataque de diccionario cancelado por el usuario.")
                            self.finished.emit()
                            return
                        if not word or not meets_password_requirements(word):
                            continue
                        attempts += 1
                        h = sha256_hash(word)
                        if h == self.target_hash:
                            elapsed = time.time() - self.start_time
                            self.found.emit(word, attempts, elapsed)
                            self.running = False
                            self.finished.emit()
                            return
                        elapsed = time.time() - self.start_time
                        self.progress.emit(attempts, self.total_candidates, elapsed)
                        if attempts % 500 == 0:
                            self.log_message(f"Probando: {word}")
        except FileNotFoundError:
            self.log_message(f"No se encontró el diccionario: {self.dictionary_path}")
        # Finalizar
        elapsed = time.time() - self.start_time
        self.progress.emit(attempts, self.total_candidates, elapsed)
        self.log_message("Ataque de diccionario finalizado sin éxito.")
        self.finished.emit()
