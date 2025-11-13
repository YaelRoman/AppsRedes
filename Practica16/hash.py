import hashlib
import sys

def hash_file(filename: str):
    # Leer el archivo en binario
    with open(filename, "rb") as f:
        data = f.read()

    md5_hash = hashlib.md5(data).hexdigest()
    sha1_hash = hashlib.sha1(data).hexdigest()
    sha256_hash = hashlib.sha256(data).hexdigest()

    print(f"Archivo: {filename}")
    print(f"MD5    : {md5_hash}")
    print(f"SHA1   : {sha1_hash}")
    print(f"SHA256 : {sha256_hash}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Uso: python {sys.argv[0]} <archivo>")
        sys.exit(1)

    hash_file(sys.argv[1])
