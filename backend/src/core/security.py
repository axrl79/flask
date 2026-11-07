import hashlib
import os
import uuid
from werkzeug.utils import secure_filename
from src.core.exceptions import FileUploadException

PDF_MAGIC_BYTES = b"%PDF-"
ALLOWED_EXTENSIONS = {"pdf"}


def is_allowed_extension(filename: str) -> bool:
    """Verifica si el nombre de archivo tiene una extensión permitida (.pdf)."""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def validate_pdf_content(stream) -> None:
    """
    Verifica que los primeros bytes del archivo correspondan al encabezado mágico de un PDF válido (%PDF-).
    Restaura el cursor al inicio del stream para lecturas posteriores.
    """
    header = stream.read(len(PDF_MAGIC_BYTES))
    stream.seek(0)
    if not header.startswith(PDF_MAGIC_BYTES):
        raise FileUploadException(
            "El archivo subido no es un documento PDF válido (encabezado corrupto o MIME inválido).",
            status_code=400,
        )


def calculate_sha256(file_path: str, chunk_size: int = 65536) -> str:
    """Calcula el hash SHA-256 de un archivo en disco por bloques para evitar saturar la memoria."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()


def generate_secure_storage_name(original_filename: str) -> str:
    """
    Genera un nombre de archivo único con UUID para almacenamiento en disco.
    Previene colisiones y ataques de Path Traversal.
    """
    safe_name = secure_filename(original_filename)
    extension = safe_name.rsplit(".", 1)[1].lower() if "." in safe_name else "pdf"
    unique_id = uuid.uuid4().hex
    return f"{unique_id}.{extension}"
