import os
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


def encrypt_aes(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    # Padding PKCS7 a bloques de 128 bits (16 bytes)
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return ciphertext


def decrypt_aes(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plain = decryptor.update(ciphertext) + decryptor.finalize()

    # Quitar padding PKCS7
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plain) + unpadder.finalize()
    return plaintext


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Uso: python {sys.argv[0]} <archivo_entrada>")
        sys.exit(1)

    in_file = sys.argv[1]

    with open(in_file, "rb") as f:
        data = f.read()

    # Clave AES-256 (32 bytes) y IV de 16 bytes
    key = os.urandom(32)
    iv = os.urandom(16)

    print(f"Clave (hex): {key.hex()}")
    print(f"IV   (hex): {iv.hex()}")

    ciphertext = encrypt_aes(key, iv, data)
    print(f"\nCifrado ({len(ciphertext)} bytes).")

    # Guardar a archivos para ver el resultado 
    with open("aes_cipher.bin", "wb") as f:
        f.write(ciphertext)

    # Descifrar
    recovered = decrypt_aes(key, iv, ciphertext)
    with open("aes_decrypted.txt", "wb") as f:
        f.write(recovered)

    print("Descifrado y guardado en 'aes_decrypted.txt'.")
