import uuid
from flask import Blueprint, request, jsonify
from src.repositories.chat_repository import ChatRepository
from src.models.chat import ChatSession, ChatMessage, QueryCitation
from src.services.rag_engine import RAGEngine
from src.core.exceptions import ValidationException, AppException

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")
chat_repo = ChatRepository()
rag_engine = RAGEngine()


@chat_bp.route("/sessions", methods=["POST"])
def create_session():
    """
    POST /api/chat/sessions
    Crea una nueva sesión de consulta técnica.
    """
    data = request.get_json(silent=True) or {}
    title = data.get("title", "Nueva Consulta Técnica").strip()
    session = ChatSession(title=title)
    chat_repo.create_session(session)
    return jsonify(session.to_dict()), 201


@chat_bp.route("/sessions", methods=["GET"])
@chat_bp.route("/history", methods=["GET"])
def list_sessions():
    """
    GET /api/chat/sessions (o /api/chat/history)
    Lista el historial de sesiones de conversación.
    """
    limit = request.args.get("limit", 50, type=int)
    sessions = chat_repo.list_sessions(limit=limit)
    return jsonify([s.to_dict() for s in sessions]), 200


@chat_bp.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    """
    GET /api/chat/sessions/<session_id>
    Obtiene los mensajes de una sesión específica con sus citas.
    """
    try:
        session_uuid = uuid.UUID(str(session_id))
    except ValueError:
        raise ValidationException("El session_id no es un UUID válido.")

    session = chat_repo.get_session(session_uuid)
    if not session:
        raise AppException(f"Sesión no encontrada: {session_id}", status_code=404)

    messages = chat_repo.get_session_messages(session_uuid)
    result = session.to_dict()
    result["messages"] = [m.to_dict() for m in messages]
    return jsonify(result), 200


@chat_bp.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    """
    DELETE /api/chat/sessions/<session_id>
    Elimina una sesión y sus mensajes asociados.
    """
    try:
        session_uuid = uuid.UUID(str(session_id))
    except ValueError:
        raise ValidationException("El session_id no es un UUID válido.")

    session = chat_repo.get_session(session_uuid)
    if not session:
        raise AppException(f"Sesión no encontrada: {session_id}", status_code=404)

    chat_repo.delete_session(session)
    return jsonify({"message": f"Sesión {session_id} eliminada exitosamente."}), 200


@chat_bp.route("/query", methods=["POST"])
def chat_query():
    """
    POST /api/chat/query
    Ejecuta una consulta fundamentada contra los manuales indexados usando RAG.
    Almacena la pregunta, respuesta y citas para auditoría técnica.
    """
    data = request.get_json()
    if not data or "query" not in data:
        raise ValidationException("El campo 'query' es obligatorio.")

    user_query = data.get("query", "").strip()
    if not user_query:
        raise ValidationException("La consulta no puede estar vacía.")

    document_id = data.get("document_id")  # Filtro opcional por manual
    top_k = data.get("top_k", 4)

    # 1. Resolver o crear sesión de chat
    session_id = data.get("session_id")
    if session_id:
        try:
            session_uuid = uuid.UUID(str(session_id))
            session = chat_repo.get_session(session_uuid)
            if not session:
                session = ChatSession(id=session_uuid, title=user_query[:50])
                chat_repo.create_session(session)
        except ValueError:
            raise ValidationException("El session_id no es un UUID válido.")
    else:
        session = ChatSession(title=user_query[:50])
        chat_repo.create_session(session)

    # 2. Registrar mensaje del usuario en PostgreSQL
    user_msg = ChatMessage(session_id=session.id, role="user", content=user_query)
    chat_repo.add_message(user_msg)

    # 3. Ejecutar inferencia RAG
    rag_result = rag_engine.query(
        question=user_query,
        document_id=document_id,
        top_k=top_k,
    )

    # 4. Registrar respuesta del asistente en PostgreSQL
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=rag_result["answer"],
        latency_seconds=rag_result["latency_seconds"],
    )
    chat_repo.add_message(assistant_msg)

    # 5. Registrar cada cita bibliográfica vinculada al mensaje
    for src in rag_result["sources"]:
        doc_uuid = None
        if src.get("document_id"):
            try:
                doc_uuid = uuid.UUID(str(src["document_id"]))
            except ValueError:
                pass

        citation = QueryCitation(
            message_id=assistant_msg.id,
            document_id=doc_uuid,
            document_name=src["document_name"],
            page_number=src["page_number"],
            chunk_id=src["chunk_id"],
            similarity_score=src["similarity_score"],
            snippet_preview=src["snippet"],
        )
        chat_repo.add_citation(citation)

    # 6. Responder payload estructurado al frontend
    return jsonify({
        "session_id": str(session.id),
        "message_id": str(assistant_msg.id),
        "query": user_query,
        "answer": rag_result["answer"],
        "sources": rag_result["sources"],
        "evidence_sufficient": rag_result["evidence_sufficient"],
        "model_used": rag_result["model_used"],
        "latency_seconds": rag_result["latency_seconds"],
    }), 200
