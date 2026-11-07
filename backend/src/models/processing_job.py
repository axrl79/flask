import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from src.extensions import db


class ProcessingJob(db.Model):
    """Registro de tareas de procesamiento e indexación RAG para auditoría y trazabilidad."""
    __tablename__ = "processing_jobs"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = db.Column(UUID(as_uuid=True), db.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)

    stage = db.Column(db.String(50), nullable=False, default="idle")
    # Etapas: idle, extracting, embedding, completed, failed

    progress_percent = db.Column(db.Integer, nullable=False, default=0)
    total_chunks_indexed = db.Column(db.Integer, nullable=False, default=0)
    error_message = db.Column(db.Text, nullable=True)

    started_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    finished_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relación
    document = db.relationship("Document", back_populates="processing_jobs")

    def to_dict(self):
        return {
            "id": str(self.id),
            "document_id": str(self.document_id),
            "stage": self.stage,
            "progress_percent": self.progress_percent,
            "total_chunks_indexed": self.total_chunks_indexed,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }
