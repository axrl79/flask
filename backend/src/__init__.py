import os
from flask import Flask
from src.config import config_by_name
from src.extensions import db, migrate, cors
from src.core.logging_config import setup_logging
from src.core.error_handlers import register_error_handlers
from src.api import documents_bp, chat_bp, system_bp, dashboard_bp

# Importar modelos para que SQLAlchemy y Flask-Migrate los reconozcan
import src.models  # noqa: F401


def create_app(config_name: str = None) -> Flask:
    """Fábrica de aplicaciones Flask (Application Factory Pattern)."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development").lower()

    app = Flask(__name__)
    config_obj = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(config_obj)

    # Configurar logging estructurado
    setup_logging(app)

    # Asegurar la creación de directorios requeridos
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["CHROMA_PERSIST_DIRECTORY"], exist_ok=True)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db, directory="migrations")
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    # Registrar manejadores de error globales
    register_error_handlers(app)

    # Registrar Blueprints de la API
    app.register_blueprint(documents_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/", methods=["GET"])
    def root():
        return {
            "name": "Plataforma RAG Manuales Industriales API",
            "version": "1.0.0",
            "status": "online",
            "docs": "/api/system/status",
        }, 200

    app.logger.info(f"Aplicación inicializada en modo: {config_name}")
    return app
