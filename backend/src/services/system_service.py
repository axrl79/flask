import os
import psutil
import urllib.request
import json
from sqlalchemy import text
from flask import current_app
from src.extensions import db


class SystemService:
    """Verificación del estado operativo de los componentes locales del sistema."""

    @staticmethod
    def get_system_status() -> dict:
        status_data = {
            "status": "healthy",
            "components": {
                "postgresql": {"status": "unknown"},
                "chromadb": {"status": "unknown"},
                "ollama": {"status": "unknown"},
            },
            "hardware": {},
        }

        # 1. Comprobar PostgreSQL
        try:
            db.session.execute(text("SELECT 1"))
            status_data["components"]["postgresql"] = {
                "status": "connected",
                "message": "Conexión a PostgreSQL 16 activa.",
            }
        except Exception as e:
            status_data["status"] = "degraded"
            status_data["components"]["postgresql"] = {
                "status": "disconnected",
                "error": str(e),
            }

        # 2. Comprobar Ollama
        ollama_url = current_app.config.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        try:
            req = urllib.request.Request(f"{ollama_url}/api/tags", headers={"User-Agent": "Flask-RAG-Backend"})
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    models = [m.get("name") for m in data.get("models", [])]
                    status_data["components"]["ollama"] = {
                        "status": "online",
                        "available_models": models,
                        "configured_embed_model": current_app.config.get("OLLAMA_EMBED_MODEL"),
                        "configured_llm_model": current_app.config.get("OLLAMA_LLM_MODEL"),
                    }
                else:
                    status_data["components"]["ollama"] = {"status": "error", "code": response.status}
        except Exception as e:
            status_data["status"] = "degraded"
            status_data["components"]["ollama"] = {
                "status": "offline",
                "error": str(e),
            }

        # 3. Comprobar ChromaDB (Directorio persistente)
        chroma_dir = current_app.config.get("CHROMA_PERSIST_DIRECTORY")
        if chroma_dir and os.path.exists(chroma_dir):
            status_data["components"]["chromadb"] = {
                "status": "ready",
                "persist_directory": chroma_dir,
            }
        else:
            status_data["components"]["chromadb"] = {
                "status": "ready_uninitialized",
                "persist_directory": chroma_dir,
            }

        # 4. Métricas de Hardware
        try:
            mem = psutil.virtual_memory()
            status_data["hardware"] = {
                "cpu_cores": psutil.cpu_count(logical=True),
                "ram_total_mb": round(mem.total / (1024 * 1024)),
                "ram_available_mb": round(mem.available / (1024 * 1024)),
                "ram_used_percent": mem.percent,
            }
        except Exception:
            status_data["hardware"] = {"info": "Información de hardware no disponible"}

        return status_data
