"""
Ventana principal del simulador de ataques de contraseña.

Esta clase define una interfaz de tablero al estilo de un «hacker» con un
tema oscuro.  Permite al usuario introducir una contraseña, evaluar su
fortaleza y visualizar varias técnicas de ataque funcionando en tiempo
real.  Cada tipo de ataque se presenta en una pestaña propia con
indicadores de progreso, gráficos y registros de actividad.
"""

import re
import string
from typing import Optional, Tuple

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTabWidget, QMessageBox, QGroupBox, QPlainTextEdit, QCheckBox
)
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp

from ..utils.hash_utils import analyze_password, sha256_hash
from ..utils.custom_generators import (
    CUSTOM_DICTIONARY_PATH,
    CUSTOM_HYBRID_BASES_PATH,
    generate_custom_files,
)
from .attack_panel import AttackPanel
from ..attacks.brute_force import BruteForceAttack
from ..attacks.dictionary_attack import DictionaryAttack
from ..attacks.hybrid_attack import HybridAttack
from ..attacks.mask_attack import MaskAttack
from ..attacks.rule_based_attack import RuleBasedAttack
from ..attacks.rainbow_table import RainbowTableAttack


ALLOWED_SPECIAL_STRING = "*. -_@=|+<>%&#$".replace(" ", "")
ALLOWED_SPECIAL_CHARACTERS = set(ALLOWED_SPECIAL_STRING)
FORBIDDEN_CHARACTERS = set("ñÑáéíóúÁÉÍÓÚ")
REQUIREMENT_DEFINITIONS = [
    ("length", "A. Debe tener exactamente 10 caracteres."),
    ("charset", "B. Debe incluir letras y dígitos, solo usar caracteres permitidos y al menos un carácter especial (* . - _ @ = | + < > % & # $)."),
    ("accents", "C. No debe contener Ñ, ñ ni vocales acentuadas."),
    ("case", "D. Debe incluir al menos una letra mayúscula y una minúscula."),
]


class DashboardWindow(QMainWindow):
    """Ventana principal con los elementos de UI y control."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Simulador de Ataques de Contraseñas")
        self.resize(1000, 800)
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        # Entrada de contraseña
        input_layout = QHBoxLayout()
        input_label = QLabel("Introduce la contraseña:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMaxLength(10)
        allowed_regex = re.escape(ALLOWED_SPECIAL_STRING)
        pattern = QRegExp(f"^[A-Za-z0-9{allowed_regex}]{{0,10}}$")
        self.password_edit.setValidator(QRegExpValidator(pattern, self))
        self.password_edit.textChanged.connect(self.on_password_input)
        self.toggle_password_button = QPushButton("Mostrar")
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.toggled.connect(self.toggle_password_visibility)
        analyze_button = QPushButton("Analizar")
        analyze_button.clicked.connect(self.analyze)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.password_edit, 1)
        input_layout.addWidget(self.toggle_password_button)
        input_layout.addWidget(analyze_button)
        layout.addLayout(input_layout)
        self._build_requirements_box(layout)
        self._build_custom_dictionary_section(layout)
        # Resumen de análisis
        self.summary_label = QLabel("Introduce una contraseña y pulsa Analizar.")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)
        # Pestañas de ataques
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)
        # Almacenar paneles
        self.attack_panels = {}

    def _build_requirements_box(self, parent_layout: QVBoxLayout) -> None:
        """Crea el cuadro que muestra el estado de los requisitos."""
        self.requirements_group = QGroupBox("Requisitos de la contraseña")
        requirements_layout = QVBoxLayout()
        self.requirement_labels = {}
        for key, description in REQUIREMENT_DEFINITIONS:
            label = QLabel(description)
            requirements_layout.addWidget(label)
            self.requirement_labels[key] = label
        self.requirements_group.setLayout(requirements_layout)
        parent_layout.addWidget(self.requirements_group)
        self._update_requirement_display("")

    def _build_custom_dictionary_section(self, parent_layout: QVBoxLayout) -> None:
        """Crea los controles para generar y activar diccionarios personalizados."""
        self.custom_group = QGroupBox("Diccionarios personalizados")
        custom_layout = QVBoxLayout()
        info_label = QLabel(
            'Introduce palabras clave separadas por comas usando el formato '
            '"word1", "word2", "word3", ...'
        )
        info_label.setWordWrap(True)
        self.keywords_edit = QPlainTextEdit()
        self.keywords_edit.setPlaceholderText('"ibero", "seguridad", "robotica"')
        generate_button = QPushButton("Generar archivos personalizados")
        generate_button.clicked.connect(self.generate_custom_dictionaries)
        self.use_custom_checkbox = QCheckBox("Usar diccionarios personalizados (si existen)")
        self.use_custom_checkbox.stateChanged.connect(self.on_custom_checkbox_changed)
        custom_layout.addWidget(info_label)
        custom_layout.addWidget(self.keywords_edit)
        custom_layout.addWidget(generate_button)
        custom_layout.addWidget(self.use_custom_checkbox)
        self.custom_group.setLayout(custom_layout)
        parent_layout.addWidget(self.custom_group)

    def _parse_keywords_input(self) -> list[str]:
        """Extrae las palabras clave del cuadro de texto."""
        raw = self.keywords_edit.toPlainText().strip()
        if not raw:
            return []
        words = []
        for part in raw.split(','):
            cleaned = part.strip().strip('"').strip("'")
            if cleaned:
                words.append(cleaned)
        return words

    def generate_custom_dictionaries(self) -> None:
        """Genera los archivos personalizados desde las palabras clave."""
        keywords = self._parse_keywords_input()
        if not keywords:
            QMessageBox.warning(
                self,
                "Sin palabras clave",
                "Introduce al menos una palabra clave en el formato indicado.",
            )
            return
        try:
            dict_path, hybrid_path = generate_custom_files(keywords)
        except ValueError as exc:
            QMessageBox.warning(self, "Error al generar", str(exc))
            return
        QMessageBox.information(
            self,
            "Diccionarios generados",
            f"Se generaron:\n- {dict_path.name}\n- {hybrid_path.name}",
        )
        self.use_custom_checkbox.blockSignals(True)
        self.use_custom_checkbox.setChecked(True)
        self.use_custom_checkbox.blockSignals(False)
        if self.password_edit.text():
            self.analyze()

    def _get_custom_paths(self) -> Tuple[Optional[str], Optional[str]]:
        """Devuelve las rutas a los archivos personalizados si deben usarse."""
        if not getattr(self, "use_custom_checkbox", None) or not self.use_custom_checkbox.isChecked():
            return None, None
        if not self._custom_files_available():
            QMessageBox.warning(
                self,
                "Archivos faltantes",
                "No se encontraron los archivos personalizados. Genera ambos antes de activarlos.",
            )
            self.use_custom_checkbox.blockSignals(True)
            self.use_custom_checkbox.setChecked(False)
            self.use_custom_checkbox.blockSignals(False)
            return None, None
        return str(CUSTOM_DICTIONARY_PATH), str(CUSTOM_HYBRID_BASES_PATH)

    def _custom_files_available(self) -> bool:
        """Indica si ambos archivos personalizados están presentes."""
        return CUSTOM_DICTIONARY_PATH.exists() and CUSTOM_HYBRID_BASES_PATH.exists()

    def on_custom_checkbox_changed(self, state: int) -> None:
        """Reacciona cuando el usuario activa/desactiva el uso de diccionarios personalizados."""
        if state and not self._custom_files_available():
            QMessageBox.warning(
                self,
                "Archivos faltantes",
                "No se encontraron los archivos personalizados. Genera ambos antes de activarlos.",
            )
            self.use_custom_checkbox.blockSignals(True)
            self.use_custom_checkbox.setChecked(False)
            self.use_custom_checkbox.blockSignals(False)
            return
        if self.password_edit.text():
            self.analyze()

    def apply_dark_theme(self) -> None:
        """Aplica un estilo oscuro al entorno (colores básicos)."""
        dark_style = """
        QWidget {
            background-color: #1e1e1e;
            color: #ccc;
        }
        QLineEdit, QPlainTextEdit, QTextEdit {
            background-color: #222;
            color: #0f0;
        }
        QPushButton {
            background-color: #333;
            color: #ccc;
            border: 1px solid #555;
            padding: 4px;
        }
        QPushButton:hover {
            background-color: #444;
        }
        QPushButton:disabled {
            background-color: #222;
            color: #555;
        }
        QProgressBar {
            background-color: #222;
            border: 1px solid #555;
            text-align: center;
            color: #ccc;
        }
        QProgressBar::chunk {
            background-color: #007700;
        }
        QTabBar::tab {
            background: #222;
            color: #ccc;
            padding: 6px;
            border: 1px solid #444;
        }
        QTabBar::tab:selected {
            background: #333;
        }
        """
        self.setStyleSheet(dark_style)

    def analyze(self) -> None:
        """Analiza la contraseña y crea los paneles de ataque."""
        pwd = self.password_edit.text()
        if not pwd:
            QMessageBox.warning(self, "Advertencia", "Introduce una contraseña para analizar.")
            return
        self._update_requirement_display(pwd)
        requirement_status = self._evaluate_password_requirements(pwd)
        if not all(requirement_status.values()):
            pending = "\n- ".join(
                desc for key, desc in REQUIREMENT_DEFINITIONS if not requirement_status.get(key, False)
            )
            QMessageBox.warning(
                self,
                "Requisitos no cumplidos",
                "La contraseña debe cumplir todos los requisitos:\n- " + pending,
            )
            return
        analysis = analyze_password(pwd)
        custom_dict_path, custom_hybrid_path = self._get_custom_paths()
        summary_lines = [
            f"Longitud: {analysis.length}",
            f"Conjuntos de caracteres usados: " + ", ".join([k for k, v in analysis.charsets.items() if v]),
            f"Entropía aproximada: {analysis.entropy_bits:.2f} bits",
            f"Categoría: {analysis.strength_category}",
        ]
        if analysis.suggestions:
            summary_lines.append("Sugerencias: " + "; ".join(analysis.suggestions))
        self.summary_label.setText("\n".join(summary_lines))
        h = sha256_hash(pwd)
        # Limpiar pestañas anteriores
        self.tabs.clear()
        self.attack_panels.clear()
        # Fuerza Bruta
        bf_panel = AttackPanel(BruteForceAttack, [h], {'alphabet': None, 'max_length': 4}, "Fuerza Bruta")
        self.tabs.addTab(bf_panel, "Fuerza Bruta")
        self.attack_panels['brute'] = bf_panel
        # Diccionario
        dict_kwargs = {}
        if custom_dict_path:
            dict_kwargs['dictionary_path'] = custom_dict_path
        dict_panel = AttackPanel(DictionaryAttack, [h], dict_kwargs, "Diccionario")
        self.tabs.addTab(dict_panel, "Diccionario")
        self.attack_panels['dictionary'] = dict_panel
        # Híbrido
        hybrid_kwargs = {'max_suffix': 200}
        if custom_hybrid_path:
            hybrid_kwargs['dictionary_path'] = custom_hybrid_path
            hybrid_kwargs['max_suffix'] = 50000
        hybrid_panel = AttackPanel(HybridAttack, [h], hybrid_kwargs, "Híbrido")
        self.tabs.addTab(hybrid_panel, "Híbrido")
        self.attack_panels['hybrid'] = hybrid_panel
        # Máscara
        mask_args = [h]
        mask_kwargs = {}
        if custom_hybrid_path:
            mask_kwargs['mask_source'] = custom_hybrid_path
        mask_panel = AttackPanel(MaskAttack, mask_args, mask_kwargs, "Máscara")
        self.tabs.addTab(mask_panel, "Máscara")
        self.attack_panels['mask'] = mask_panel
        # Reglas
        rule_kwargs = {}
        if custom_dict_path:
            rule_kwargs['dictionary_path'] = custom_dict_path
        rule_panel = AttackPanel(RuleBasedAttack, [h], rule_kwargs, "Reglas")
        self.tabs.addTab(rule_panel, "Reglas")
        self.attack_panels['rule'] = rule_panel
        # Tabla arcoíris
        rainbow_panel = AttackPanel(RainbowTableAttack, [h], {}, "Tabla Arcoíris")
        self.tabs.addTab(rainbow_panel, "Arcoíris")
        self.attack_panels['rainbow'] = rainbow_panel

    def on_password_input(self, text: str) -> None:
        """Actualiza el estado de los requisitos mientras se escribe."""
        self._update_requirement_display(text)

    def _evaluate_password_requirements(self, password: str) -> dict[str, bool]:
        """Determina si la contrasena escrita cumple cada requisito."""
        letters_digits = set(string.ascii_letters + string.digits)
        only_allowed = all((ch in letters_digits) or (ch in ALLOWED_SPECIAL_CHARACTERS) for ch in password)
        has_special = any(ch in ALLOWED_SPECIAL_CHARACTERS for ch in password)
        has_digit = any(ch.isdigit() for ch in password)
        has_upper = any(ch.isupper() for ch in password)
        has_lower = any(ch.islower() for ch in password)
        return {
            "length": len(password) == 10,
            "charset": bool(password) and only_allowed and has_special and has_digit,
            "accents": not any(ch in FORBIDDEN_CHARACTERS for ch in password),
            "case": has_upper and has_lower,
        }

    def _update_requirement_display(self, password: str) -> None:
        """Refresca el cuadro informativo de requisitos."""
        if not hasattr(self, "requirement_labels"):
            return
        status = self._evaluate_password_requirements(password)
        description_lookup = {key: desc for key, desc in REQUIREMENT_DEFINITIONS}
        for key, label in self.requirement_labels.items():
            met = status.get(key, False)
            suffix = " [OK]" if met else " [Pendiente]"
            label.setText(description_lookup[key] + suffix)
            label.setStyleSheet("color: #4caf50;" if met else "color: #ff7676;")

    def toggle_password_visibility(self, checked: bool) -> None:
        """Muestra u oculta la contraseña introducida."""
        self.password_edit.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.toggle_password_button.setText("Ocultar" if checked else "Mostrar")


def run_app() -> None:
    """Lanza la aplicación."""
    import sys
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.apply_dark_theme()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()
