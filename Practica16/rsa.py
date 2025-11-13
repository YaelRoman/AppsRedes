import sys

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


def load_public_key(path: str):
    with open(path, "rb") as f:
        pem_data = f.read()
    public_key = serialization.load_pem_public_key(pem_data)
    return public_key


def load_private_key(path: str):
    with open(path, "rb") as f:
        pem_data = f.read()
    # Si tu llave privada tiene passphrase, pásala aquí en password=b"..."
    private_key = serialization.load_pem_private_key(pem_data, password=None)
    return private_key


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Uso: python {sys.argv[0]} <archivo_entrada_pequeño>")
        sys.exit(1)

    in_file = sys.argv[1]

    with open(in_file, "rb") as f:
        message = f.read()

    # 1) Cargar llaves
    public_key = load_public_key("rsa_publica.pem")
    private_key = load_private_key("rsa_privada.pem")

    # 2) Cifrar con la llave pública (RSA + OAEP + SHA256)
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    with open("rsa_cipher.bin", "wb") as f:
        f.write(ciphertext)
    print(f"Cifrado con RSA ({len(ciphertext)} bytes) -> 'rsa_cipher.bin'")

    # 3) Descifrar con la llave privada
    recovered = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    with open("rsa_decrypted.txt", "wb") as f:
        f.write(recovered)
    print("Descifrado y guardado en 'rsa_decrypted.txt'.")
