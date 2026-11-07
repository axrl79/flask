from flask import Blueprint, jsonify
from sqlalchemy import func
from src.extensions import db
from src.models.document import Document
from src.models.chat import ChatMessage, ChatSession

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/stats", methods=["GET"])
def get_dashboard_stats():
    """
    GET /api/dashboard/stats
    Retorna métricas agregadas del sistema para el panel de control.
    """
    total_docs = db.session.query(func.count(Document.id)).scalar() or 0
    indexed_docs = db.session.query(func.count(Document.id)).filter(Document.status == "indexed").scalar() or 0
    total_pages = db.session.query(func.sum(Document.total_pages)).scalar() or 0
    total_storage_bytes = db.session.query(func.sum(Document.file_size_bytes)).scalar() or 0

    total_sessions = db.session.query(func.count(ChatSession.id)).scalar() or 0
    total_queries = db.session.query(func.count(ChatMessage.id)).filter(ChatMessage.role == "user").scalar() or 0

    return jsonify({
        "documents": {
            "total": total_docs,
            "indexed": indexed_docs,
            "total_pages": int(total_pages),
            "storage_bytes": int(total_storage_bytes),
            "storage_mb": round(int(total_storage_bytes) / (1024 * 1024), 2),
        },
        "chat": {
            "total_sessions": total_sessions,
            "total_queries": total_queries,
        },
    }), 200
