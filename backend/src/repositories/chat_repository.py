from typing import List, Optional
from uuid import UUID
from src.extensions import db
from src.models.chat import ChatSession, ChatMessage, QueryCitation


class ChatRepository:
    """Acceso a datos para sesiones de chat, mensajes y citas técnicas."""

    @staticmethod
    def get_session(session_id: UUID) -> Optional[ChatSession]:
        return db.session.get(ChatSession, session_id)

    @staticmethod
    def list_sessions(limit: int = 50) -> List[ChatSession]:
        return ChatSession.query.order_by(ChatSession.updated_at.desc()).limit(limit).all()

    @staticmethod
    def create_session(session: ChatSession) -> ChatSession:
        db.session.add(session)
        db.session.commit()
        return session

    @staticmethod
    def delete_session(session: ChatSession) -> None:
        db.session.delete(session)
        db.session.commit()

    @staticmethod
    def add_message(message: ChatMessage) -> ChatMessage:
        db.session.add(message)
        db.session.commit()
        return message

    @staticmethod
    def add_citation(citation: QueryCitation) -> QueryCitation:
        db.session.add(citation)
        db.session.commit()
        return citation

    @staticmethod
    def get_session_messages(session_id: UUID) -> List[ChatMessage]:
        return (
            ChatMessage.query.filter_by(session_id=session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
