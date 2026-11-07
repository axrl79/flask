import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables desde el archivo .env ubicado en backend/
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Configuración base de la aplicación."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-rag-industrial-2026")
    DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")

    # SQLAlchemy y PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_industrial"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Rutas de almacenamiento local
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "storage" / "uploads"))
    if not os.path.isabs(UPLOAD_FOLDER):
        UPLOAD_FOLDER = str(BASE_DIR / UPLOAD_FOLDER)

    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", str(BASE_DIR / "storage" / "chroma"))
    if not os.path.isabs(CHROMA_PERSIST_DIRECTORY):
        CHROMA_PERSIST_DIRECTORY = str(BASE_DIR / CHROMA_PERSIST_DIRECTORY)

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 50 * 1024 * 1024))  # 50 MB

    # Configuración de Ollama Local
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3.1:8b")

    # CORS
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_industrial_test"
    )


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
