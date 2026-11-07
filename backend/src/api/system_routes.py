from flask import Blueprint, jsonify
from src.services.system_service import SystemService

system_bp = Blueprint("system", __name__, url_prefix="/api/system")


@system_bp.route("/status", methods=["GET"])
def get_system_status():
    """
    GET /api/system/status
    Comprueba y retorna el estado de PostgreSQL, Ollama, ChromaDB y recursos del host.
    """
    status_data = SystemService.get_system_status()
    http_code = 200 if status_data["status"] == "healthy" else 503
    return jsonify(status_data), http_code
