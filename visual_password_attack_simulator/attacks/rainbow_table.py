"""
Implementación de un ataque tipo tabla arcoíris (rainbow table).

Una tabla arcoíris es una estructura precomputada que almacena
contraseñas en texto claro junto con sus hashes, lo que permite la
recuperación rápida de contraseñas conocidas.  En esta simulación se
utiliza una pequeña tabla en memoria cargada desde un archivo para
demostrar la diferencia de rendimiento con respecto a ataques que
necesitan calcular hashes para cada intento.
"""

import time
from pathlib import Path
from typing import Optional

from .base_attack import AttackThread
from ..utils.password_requirements import meets_password_requirements


class RainbowTableAttack(AttackThread):
    """Ataque que utiliza una tabla precomputada de hashes."""

    def __init__(self, target_hash: str, table_path: Optional[str] = None) -> None:
        super().__init__(target_hash)
        if table_path is None:
            table_path = Path(__file__).resolve().parent.parent / "rainbow_table.txt"
        self.table_path = Path(table_path)
        self.rainbow_map = {}  # hash -> contraseña
        self.total_candidates = 0
        self._load_table()

    def _load_table(self) -> None:
        """Carga la tabla de hashes desde disco."""
        try:
            with self.table_path.open('r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        h, pwd = line.split(':', 1)
                        if meets_password_requirements(pwd):
                            self.rainbow_map[h] = pwd
                self.total_candidates = len(self.rainbow_map)
        except FileNotFoundError:
            self.log_message(f"No se encontró la tabla arcoíris: {self.table_path}")

    def run(self) -> None:
        self.start_time = time.time()
        attempts = 0
        # La tabla arcoíris permite consulta directa
        elapsed = 0.0
        if self.target_hash in self.rainbow_map:
            password = self.rainbow_map[self.target_hash]
            attempts = 1
            elapsed = time.time() - self.start_time
            self.found.emit(password, attempts, elapsed)
        else:
            attempts = len(self.rainbow_map)
            elapsed = time.time() - self.start_time
            self.log_message("La contraseña no está en la tabla arcoíris.")
        # Emitir progreso final
        self.progress.emit(attempts, self.total_candidates, elapsed)
        self.finished.emit()
