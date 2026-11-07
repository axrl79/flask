import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from src.extensions import db


class Document(db.Model):
    """Modelo relacional para documentos técnicos (manuales PDF)."""
    __tablename__ = "documents"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = db.Column(db.String(255), nullable=False)  # Nombre físico seguro en almacenamiento
    original_filename = db.Column(db.String(255), nullable=False)  # Nombre original subido por el técnico
    file_path = db.Column(db.String(512), nullable=False)
    file_hash_sha256 = db.Column(db.String(64), nullable=False, unique=True, index=True)
    file_size_bytes = db.Column(db.BigInteger, nullable=False)
    total_pages = db.Column(db.Integer, nullable=False, default=0)
    mime_type = db.Column(db.String(100), nullable=False, default="application/pdf")
    status = db.Column(db.String(50), nullable=False, default="uploaded", index=True)
    # Estados permitidos: uploaded, processing, indexed, failed

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    processing_jobs = db.relationship("ProcessingJob", back_populates="document", cascade="all, delete-orphan", lazy="dynamic")
    sections = db.relationship("DocumentSection", back_populates="document", cascade="all, delete-orphan", lazy="dynamic")
    citations = db.relationship("QueryCitation", back_populates="document", lazy="dynamic")

    def to_dict(self):
        """Serializa la entidad a un diccionario para respuestas JSON."""
        latest_job = self.processing_jobs.order_by(db.desc(ProcessingJob.started_at)).first() if hasattr(self, 'processing_jobs') else None
        return {
            "id": str(self.id),
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size_bytes": self.file_size_bytes,
            "total_pages": self.total_pages,
            "mime_type": self.mime_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "chunks_count": latest_job.total_chunks_indexed if latest_job else 0,
        }


# Importar aquí para evitar referencias circulares en type hints de to_dict
from src.models.processing_job import ProcessingJob  # noqa: E402
