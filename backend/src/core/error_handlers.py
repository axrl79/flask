from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
from src.core.exceptions import AppException


def register_error_handlers(app):
    """Registra manejadores de error centralizados para devolver respuestas JSON coherentes."""

    @app.errorhandler(AppException)
    def handle_app_exception(error):
        current_app.logger.warning(f"AppException [{error.code}]: {error.message} (Detalles: {error.details})")
        response = {
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details,
            }
        }
        return jsonify(response), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        current_app.logger.warning(f"HTTPException [{error.code}]: {error.description}")
        response = {
            "error": {
                "code": error.name.upper().replace(" ", "_"),
                "message": error.description,
            }
        }
        return jsonify(response), error.code

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        current_app.logger.exception(f"Error no controlado en el servidor: {str(error)}")
        response = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Ha ocurrido un error inesperado en el servidor.",
            }
        }
        return jsonify(response), 500
