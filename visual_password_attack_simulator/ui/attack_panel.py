"""
Componente gráfico reutilizable para representar un ataque individual en la
interfaz.  Cada panel muestra controles para iniciar y detener el ataque,
una barra de progreso, estadísticas de intentos y tiempo, un área de log
tipo terminal y un gráfico simple de velocidad de intentos por segundo.
"""

from typing import Type, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QPlainTextEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSlot
import pyqtgraph as pg

from ..attacks.base_attack import AttackThread


class AttackPanel(QWidget):
    """Panel que gestiona la ejecución y visualización de un ataque."""

    def __init__(self, attack_cls: Type[AttackThread], attack_args: list, attack_kwargs: dict, nombre: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.attack_cls = attack_cls
        self.attack_args = attack_args
        self.attack_kwargs = attack_kwargs
        self.attack_thread: Optional[AttackThread] = None
        self.nombre = nombre
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        title = QLabel(self.nombre)
        title.setStyleSheet("color: #00FF00; font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        # Controles de botones
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Iniciar")
        self.start_btn.clicked.connect(self.start_attack)
        self.stop_btn = QPushButton("Detener")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_attack)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        # Estadísticas
        stats_layout = QHBoxLayout()
        self.attempts_label = QLabel("Intentos: 0")
        self.time_label = QLabel("Tiempo: 0.0s")
        self.rate_label = QLabel("Velocidad: 0/s")
        stats_layout.addWidget(self.attempts_label)
        stats_layout.addWidget(self.time_label)
        stats_layout.addWidget(self.rate_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        # Área de log tipo terminal
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        font = self.log_area.font()
        font.setFamily("Courier")
        self.log_area.setFont(font)
        self.log_area.setStyleSheet("background-color: #111; color: #0f0;")
        self.log_area.setLineWrapMode(QPlainTextEdit.NoWrap)
        layout.addWidget(self.log_area)
        # Gráfico de velocidad
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#222')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Intentos/segundo')
        self.plot_widget.setLabel('bottom', 'Segundos')
        self.curve = self.plot_widget.plot(pen=pg.mkPen('lime'))
        # Datos de gráfica
        self.times: list = []
        self.rates: list = []
        layout.addWidget(self.plot_widget)

    @pyqtSlot()
    def start_attack(self) -> None:
        """Instancia y lanza el hilo del ataque."""
        if self.attack_thread and self.attack_thread.isRunning():
            return
        # Reset UI
        self.log_area.clear()
        self.progress_bar.setValue(0)
        self.attempts_label.setText("Intentos: 0")
        self.time_label.setText("Tiempo: 0.0s")
        self.rate_label.setText("Velocidad: 0/s")
        self.times = []
        self.rates = []
        self.curve.setData([], [])
        # Crear hilo
        self.attack_thread = self.attack_cls(*self.attack_args, **self.attack_kwargs)
        self.attack_thread.progress.connect(self.on_progress)
        self.attack_thread.found.connect(self.on_found)
        self.attack_thread.log.connect(self.on_log)
        self.attack_thread.finished.connect(self.on_finished)
        self.attack_thread.start()
        # Actualizar botones
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    @pyqtSlot()
    def stop_attack(self) -> None:
        """Solicita la detención del hilo."""
        if self.attack_thread:
            self.attack_thread.stop()
        self.stop_btn.setEnabled(False)

    @pyqtSlot(int, int, float)
    def on_progress(self, attempts: int, total: int, elapsed: float) -> None:
        """Actualiza la interfaz con el progreso del ataque."""
        self.attempts_label.setText(f"Intentos: {attempts}")
        self.time_label.setText(f"Tiempo: {elapsed:.1f}s")
        rate = attempts / elapsed if elapsed > 0 else 0.0
        self.rate_label.setText(f"Velocidad: {rate:.1f}/s")
        # Actualizar barra de progreso si se conoce el total
        if total > 0:
            value = int(min(100, attempts / total * 100))
            self.progress_bar.setValue(value)
        # Añadir datos a la gráfica cada cierto número de muestras
        if len(self.times) == 0 or (elapsed - self.times[-1] >= 0.5):
            self.times.append(elapsed)
            self.rates.append(rate)
            self.curve.setData(self.times, self.rates)

    @pyqtSlot(str, int, float)
    def on_found(self, password: str, attempts: int, elapsed: float) -> None:
        """Muestra el resultado cuando se encuentra la contraseña."""
        self.log_area.appendPlainText(f"\n>>> Contraseña encontrada: {password} (intentos: {attempts}, tiempo: {elapsed:.2f}s)")
        # Destacar visualmente el panel (por ejemplo, cambiar color de fondo de la barra)
        self.progress_bar.setStyleSheet("QProgressBar::chunk{background-color:#0f0;}QProgressBar{background-color:#222;color:#fff;}")

    @pyqtSlot(str)
    def on_log(self, message: str) -> None:
        """Añade un mensaje al log."""
        self.log_area.appendPlainText(message)
        # Desplazarse al final
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    @pyqtSlot()
    def on_finished(self) -> None:
        """Se ejecuta cuando el hilo finaliza (con éxito o no)."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)