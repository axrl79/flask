import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from src.extensions import db


class ChatSession(db.Model):
    """Sesión de conversación técnica para agrupar consultas de un técnico."""
    __tablename__ = "chat_sessions"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False, default="Nueva Consulta Técnica")

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relación
    messages = db.relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "message_count": self.messages.count(),
        }


class ChatMessage(db.Model):
    """Mensaje individual en una sesión (pregunta del técnico o respuesta del asistente)."""
    __tablename__ = "chat_messages"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)

    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    latency_seconds = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones
    session = db.relationship("ChatSession", back_populates="messages")
    citations = db.relationship("QueryCitation", back_populates="message", cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self):
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "role": self.role,
            "content": self.content,
            "latency_seconds": self.latency_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "citations": [c.to_dict() for c in self.citations.all()],
        }


class QueryCitation(db.Model):
    """Referencia exacta y fundamentada (documento, página, fragmento) de una respuesta generada."""
    __tablename__ = "query_citations"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = db.Column(UUID(as_uuid=True), db.ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = db.Column(UUID(as_uuid=True), db.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)

    document_name = db.Column(db.String(255), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    chunk_id = db.Column(db.String(128), nullable=False)
    similarity_score = db.Column(db.Float, nullable=False, default=0.0)
    snippet_preview = db.Column(db.Text, nullable=False)

    # Relaciones
    message = db.relationship("ChatMessage", back_populates="citations")
    document = db.relationship("Document", back_populates="citations")

    def to_dict(self):
        return {
            "id": str(self.id),
            "message_id": str(self.message_id),
            "document_id": str(self.document_id) if self.document_id else None,
            "document_name": self.document_name,
            "page_number": self.page_number,
            "chunk_id": self.chunk_id,
            "similarity_score": self.similarity_score,
            "snippet_preview": self.snippet_preview,
        }
