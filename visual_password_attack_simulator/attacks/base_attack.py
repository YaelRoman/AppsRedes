"""
Módulo base para los ataques de contraseñas.

Contiene la clase `AttackThread`, una subclase de QThread que define la
interfaz común para las diferentes estrategias de ataque implementadas en el
simulador.  Cada ataque debe heredar de `AttackThread` y sobrescribir el
método `run` para realizar la búsqueda concreta.  Los ataques emiten
señales para informar al interfaz gráfico sobre el progreso y el resultado.
"""

import time
from typing import Optional

from PyQt5.QtCore import QThread, pyqtSignal


class AttackThread(QThread):
    """Hilo base para ejecutar un ataque contra un hash.

    Atributos:
        target_hash: El hash SHA‑256 de la contraseña que se intenta descubrir.
        running: Bandera que indica si el hilo debe seguir ejecutándose.
        start_time: Marca de tiempo al inicio del ataque.

    Señales:
        progress(int, int, float): número de intentos realizados, total
            estimado (puede ser 0 si no se conoce) y segundos transcurridos.
        found(str, int, float): emitida cuando se descubre la contraseña.
        log(str): mensajes de log o depuración.
        finished(): cuando el ataque finaliza (éxito o no).
    """
    progress = pyqtSignal(int, int, float)
    found = pyqtSignal(str, int, float)
    log = pyqtSignal(str)

    def __init__(self, target_hash: str, parent: Optional[object] = None) -> None:
        super().__init__(parent)
        self.target_hash = target_hash
        self.running = True
        self.start_time: float = 0.0
        self.total_candidates: int = 0  # Si se conoce de antemano

    def stop(self) -> None:
        """Solicita la detención del hilo."""
        self.running = False

    def log_message(self, message: str) -> None:
        """Envía un mensaje de log a través de la señal correspondiente."""
        self.log.emit(message)

    # Método run a implementar por cada subclase
    def run(self) -> None:  # pragma: no cover
        raise NotImplementedError