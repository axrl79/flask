import logging
import sys


def setup_logging(app):
    """Configura el registro de logs estructurado para la aplicación Flask."""
    log_level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s in %(filename)s:%(lineno)d]: %(message)s"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)

    # Configurar logger raíz de la aplicación
    app.logger.setLevel(log_level)
    if not app.logger.handlers:
        app.logger.addHandler(handler)

    # Reducir verbosidad de werkzeug si no estamos en debug profundo
    logging.getLogger("werkzeug").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
