import mimetypes
import smtplib
from email.message import EmailMessage
from pathlib import Path

try:
    from cryptography.fernet import Fernet
except ImportError as exc:
    raise SystemExit(
        "Instala la libreria 'cryptography' para usar el cifrado del password (pip install cryptography)."
    ) from exc


BASE_DIR = Path(__file__).resolve().parent
HTML_BODY_PATH = BASE_DIR / "email_body.html"
PASSWORD_KEY_PATH = BASE_DIR / "smtp_password.key"
PASSWORD_ENC_PATH = BASE_DIR / "smtp_password.enc"
ATTACHMENTS = [
    BASE_DIR / "adjuntos" / "IMPORTANTE.pdf",
]
RECIPIENTS = [
    "p37676@correo.uia.mx",
    "a2305103@correo.uia.mx",
    "a2585732@correo.uia.mx",
    "a2300592@correo.uia.mx",
    "a231592a@correo.uia.mx",
]
SENDER = "ibero.contacto.computo@gmail.com"
SUBJECT = "Información importante sobre tu cuenta"


def decrypt_password(key_path: Path, token_path: Path) -> str:
    """Recupera el password cifrado usando Fernet."""
    if not key_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo con la llave: {key_path}")
    if not token_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo con el password cifrado: {token_path}")
    cipher = Fernet(key_path.read_bytes())
    decrypted = cipher.decrypt(token_path.read_bytes())
    return decrypted.decode("utf-8")


def load_html_body(html_path: Path) -> str:
    """Carga el contenido HTML del correo desde archivo."""
    if not html_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo con el cuerpo del correo: {html_path}")
    return html_path.read_text(encoding="utf-8")


def attach_files(message: EmailMessage, attachment_paths: list[Path]) -> None:
    """Adjunta los archivos indicados, ignorando los que no existan."""
    for path in attachment_paths:
        if not path.exists():
            print(f"Aviso: no se encontró el adjunto {path}, se omite.")
            continue
        content_type, _ = mimetypes.guess_type(path.name)
        maintype, subtype = ("application", "octet-stream")
        if content_type:
            maintype, subtype = content_type.split("/", 1)
        message.add_attachment(
            path.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=path.name,
        )


def main() -> None:
    password = decrypt_password(PASSWORD_KEY_PATH, PASSWORD_ENC_PATH)
    html_body = load_html_body(HTML_BODY_PATH)

    mensaje = EmailMessage()
    mensaje["Subject"] = SUBJECT
    mensaje["From"] = SENDER
    mensaje["To"] = ", ".join(RECIPIENTS)
    mensaje.set_content("Tu cliente de correo no soporta contenido HTML.")
    mensaje.add_alternative(html_body, subtype="html")
    attach_files(mensaje, ATTACHMENTS)

    with smtplib.SMTP("smtp.gmail.com", 587) as servidor_smtp:
        servidor_smtp.ehlo()
        servidor_smtp.starttls()
        servidor_smtp.login(SENDER, password)
        servidor_smtp.send_message(mensaje)

    print("Mensaje enviado")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error al enviar correo: {exc}")
