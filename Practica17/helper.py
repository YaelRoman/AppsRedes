from cryptography.fernet import Fernet
from pathlib import Path

base = Path("Practica17")
key_path = base / "smtp_password.key"
token_path = base / "smtp_password.enc"
password = "pass"  

key = Fernet.generate_key()
key_path.write_bytes(key)

cipher = Fernet(key)
token = cipher.encrypt(password.encode("utf-8"))
token_path.write_bytes(token)

print(f"Key guardada en {key_path}")
print(f"Password cifrado guardado en {token_path}")
