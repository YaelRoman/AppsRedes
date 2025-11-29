#!/usr/bin/env python3
"""
generate_rainbow_table.py

Genera una tabla tipo rainbow (muy simplificada) a partir de un diccionario
de contraseñas. Para cada contraseña se calcula su hash SHA-256 y se guarda
la pareja hash:contraseña en un archivo de salida.

Formato de salida (texto plano):
    <hash_hex>:<password>

Uso educativo para el proyecto en IberoCDMX:
- No está pensado para ataques reales a sistemas de terceros.
- Solo se recomienda usarlo con contraseñas de prueba (de laboratorio).
"""

import hashlib
from pathlib import Path

# ==========================
# Parámetros de configuración
# ==========================

HERE = Path(__file__).resolve().parent
INPUT_DICTIONARY = HERE / "dictionary.txt"      # debe existir
OUTPUT_RAINBOW = HERE / "rainbow_table.txt"     # se creará / sobrescribirá


def sha256_hex(text: str) -> str:
    """
    Devuelve el hash SHA-256 en hexadecimal de la cadena de entrada.
    """
    h = hashlib.sha256()
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def main():
    if not INPUT_DICTIONARY.exists():
        print(f"[ERROR] No se encontró el diccionario: {INPUT_DICTIONARY}")
        print("        Ejecuta primero generate_dictionary.py o ajusta la ruta.")
        return

    print(f"[INFO] Leyendo diccionario desde: {INPUT_DICTIONARY.resolve()}")

    count = 0
    with INPUT_DICTIONARY.open("r", encoding="utf-8") as fin, \
            OUTPUT_RAINBOW.open("w", encoding="utf-8") as fout:

        for line in fin:
            pwd = line.strip()
            if not pwd:
                continue
            h = sha256_hex(pwd)
            fout.write(f"{h}:{pwd}\n")
            count += 1
            if count % 500 == 0:
                print(f"[INFO] Procesadas {count} contraseñas...")

    print(f"[OK] Rainbow table generada en: {OUTPUT_RAINBOW.resolve()}")
    print(f"[OK] Total de entradas: {count}")


if __name__ == "__main__":
    main()
