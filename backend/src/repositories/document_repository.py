from typing import List, Optional
from uuid import UUID
from sqlalchemy import or_
from src.extensions import db
from src.models.document import Document
from src.models.processing_job import ProcessingJob


class DocumentRepository:
    """Acceso a datos para documentos técnicos y sus jobs de procesamiento."""

    @staticmethod
    def get_by_id(document_id: UUID) -> Optional[Document]:
        return db.session.get(Document, document_id)

    @staticmethod
    def get_by_hash(file_hash: str) -> Optional[Document]:
        return Document.query.filter_by(file_hash_sha256=file_hash).first()

    @staticmethod
    def list_all(status: Optional[str] = None, search: Optional[str] = None) -> List[Document]:
        query = Document.query
        if status:
            query = query.filter_by(status=status)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Document.original_filename.ilike(search_term),
                    Document.filename.ilike(search_term),
                )
            )
        return query.order_by(Document.created_at.desc()).all()

    @staticmethod
    def create(document: Document) -> Document:
        db.session.add(document)
        db.session.commit()
        return document

    @staticmethod
    def update(document: Document) -> Document:
        db.session.commit()
        return document

    @staticmethod
    def delete(document: Document) -> None:
        db.session.delete(document)
        db.session.commit()

    @staticmethod
    def create_job(job: ProcessingJob) -> ProcessingJob:
        db.session.add(job)
        db.session.commit()
        return job

    @staticmethod
    def update_job(job: ProcessingJob) -> ProcessingJob:
        db.session.commit()
        return job
