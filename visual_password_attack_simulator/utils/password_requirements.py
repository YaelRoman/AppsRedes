"""
Herramientas compartidas para la política de contraseñas del simulador.

Este módulo centraliza los requisitos que debe cumplir cualquier
contraseña válida tanto para la interfaz de usuario como para los
distintos ataques.  Al concentrar la lógica en un lugar podemos mantener
el comportamiento coherente en todo el proyecto.
"""

from __future__ import annotations

import string
from typing import List

# Requisitos fijos
PASSWORD_LENGTH = 10
ALLOWED_SPECIAL_CHARACTERS = "*.-_@=|+<>%&#$"
FORBIDDEN_CHARACTERS = set("ÑñáéíóúÁÉÍÓÚ")
ALLOWED_CHARACTERS = string.ascii_letters + string.digits + ALLOWED_SPECIAL_CHARACTERS


def meets_password_requirements(password: str) -> bool:
    """Comprueba si una contraseña cumple la política declarada."""
    if len(password) != PASSWORD_LENGTH:
        return False
    if any(ch in FORBIDDEN_CHARACTERS for ch in password):
        return False
    if not all(ch in ALLOWED_CHARACTERS for ch in password):
        return False
    if not any(ch.islower() for ch in password):
        return False
    if not any(ch.isupper() for ch in password):
        return False
    if not any(ch.isdigit() for ch in password):
        return False
    if not any(ch in ALLOWED_SPECIAL_CHARACTERS for ch in password):
        return False
    return True


def unmet_requirements(password: str) -> List[str]:
    """Devuelve una lista de requisitos no cumplidos (para mensajes)."""
    missing: List[str] = []
    if len(password) != PASSWORD_LENGTH:
        missing.append(f"Tener exactamente {PASSWORD_LENGTH} caracteres.")
    if any(ch in FORBIDDEN_CHARACTERS for ch in password):
        missing.append("No contener Ñ, ñ ni vocales acentuadas.")
    if not all(ch in ALLOWED_CHARACTERS for ch in password):
        missing.append("Usar únicamente dígitos, letras o los caracteres especiales permitidos.")
    if not any(ch.islower() for ch in password):
        missing.append("Incluir al menos una letra minúscula.")
    if not any(ch.isupper() for ch in password):
        missing.append("Incluir al menos una letra mayúscula.")
    if not any(ch.isdigit() for ch in password):
        missing.append("Incorporar al menos un dígito.")
    if not any(ch in ALLOWED_SPECIAL_CHARACTERS for ch in password):
        missing.append("Agregar al menos un carácter especial permitido (* . - _ @ = | + < > % & # $).")
    return missing


__all__ = [
    "PASSWORD_LENGTH",
    "ALLOWED_SPECIAL_CHARACTERS",
    "FORBIDDEN_CHARACTERS",
    "ALLOWED_CHARACTERS",
    "meets_password_requirements",
    "unmet_requirements",
]
