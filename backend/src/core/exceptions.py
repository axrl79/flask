"""Módulo de excepciones de dominio para la plataforma RAG."""

class AppException(Exception):
    """Excepción base de la aplicación."""
    status_code = 500
    code = "INTERNAL_SERVER_ERROR"

    def __init__(self, message: str, status_code: int = None, details=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.details = details or {}


class ValidationException(AppException):
    status_code = 400
    code = "VALIDATION_ERROR"


class FileUploadException(AppException):
    status_code = 400
    code = "FILE_UPLOAD_ERROR"


class DocumentDuplicateException(AppException):
    status_code = 409
    code = "DOCUMENT_DUPLICATE"


class DocumentNotFoundException(AppException):
    status_code = 404
    code = "DOCUMENT_NOT_FOUND"


class DatabaseConnectionException(AppException):
    status_code = 503
    code = "DATABASE_UNAVAILABLE"


class ServiceUnavailableException(AppException):
    status_code = 503
    code = "SERVICE_UNAVAILABLE"
