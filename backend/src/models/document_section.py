import uuid
from sqlalchemy.dialects.postgresql import UUID
from src.extensions import db


class DocumentSection(db.Model):
    """Estructura de secciones y páginas de un documento para trazabilidad."""
    __tablename__ = "document_sections"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = db.Column(UUID(as_uuid=True), db.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)

    page_number = db.Column(db.Integer, nullable=False)
    chunks_count = db.Column(db.Integer, nullable=False, default=0)
    has_tables = db.Column(db.Boolean, nullable=False, default=False)

    # Relación
    document = db.relationship("Document", back_populates="sections")

    def to_dict(self):
        return {
            "id": str(self.id),
            "document_id": str(self.document_id),
            "page_number": self.page_number,
            "chunks_count": self.chunks_count,
            "has_tables": self.has_tables,
        }
