import os
import uuid
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
import pymupdf  # Modern PyMuPDF API
from flask import current_app
from werkzeug.datastructures import FileStorage

from src.core.exceptions import (
    DocumentDuplicateException,
    DocumentNotFoundException,
    FileUploadException,
    ValidationException,
    AppException,
)
from src.core.security import (
    calculate_sha256,
    generate_secure_storage_name,
    is_allowed_extension,
    validate_pdf_content,
)
from src.extensions import db
from src.models.document import Document
from src.models.processing_job import ProcessingJob
from src.models.document_section import DocumentSection
from src.repositories.document_repository import DocumentRepository
from src.services.pdf_extractor import PDFExtractor
from src.services.text_splitter import TokenAwareTextSplitter
from src.services.chroma_service import ChromaService
from src.services.ollama_service import OllamaService


class DocumentService:
    """Lógica de negocio para gestión, almacenamiento seguro, extracción e indexación RAG de manuales técnicos."""

    def __init__(
        self,
        repo: Optional[DocumentRepository] = None,
        chroma_service: Optional[ChromaService] = None,
        ollama_service: Optional[OllamaService] = None,
    ):
        self.repo = repo or DocumentRepository()
        self.chroma = chroma_service or ChromaService()
        self.ollama = ollama_service or OllamaService()
        self.text_splitter = TokenAwareTextSplitter(target_chunk_tokens=550, overlap_tokens=90)

    def upload_document(self, file_storage: FileStorage) -> Document:
        """Valida, almacena en disco y registra un manual técnico en PostgreSQL."""
        if not file_storage or not file_storage.filename:
            raise ValidationException("No se proporcionó ningún archivo para subir.")

        original_filename = file_storage.filename.strip()

        # 1. Validar extensión permitida
        if not is_allowed_extension(original_filename):
            raise FileUploadException(
                f"Formato no permitido para '{original_filename}'. Únicamente se admiten archivos .pdf.",
                status_code=400,
            )

        # 2. Validar contenido real (Magic bytes %PDF-)
        validate_pdf_content(file_storage.stream)

        # 3. Preparar ruta de almacenamiento seguro
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        secure_name = generate_secure_storage_name(original_filename)
        file_path = os.path.join(upload_folder, secure_name)

        # 4. Guardar archivo en disco
        file_storage.save(file_path)
        file_size = os.path.getsize(file_path)

        # 5. Calcular SHA-256 para control de integridad y duplicidad
        file_hash = calculate_sha256(file_path)

        # 6. Comprobar duplicado en la base de datos
        existing_doc = self.repo.get_by_hash(file_hash)
        if existing_doc:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise DocumentDuplicateException(
                f"El documento '{original_filename}' ya existe en el sistema con el ID: {existing_doc.id}.",
                details={"existing_document_id": str(existing_doc.id)},
            )

        # 7. Extraer metadatos iniciales del PDF (número de páginas con PyMuPDF)
        total_pages = 0
        try:
            with pymupdf.open(file_path) as doc:
                total_pages = doc.page_count
        except Exception as e:
            current_app.logger.warning(f"No se pudo determinar el total de páginas con PyMuPDF: {str(e)}")

        # 8. Persistir en PostgreSQL
        new_document = Document(
            filename=secure_name,
            original_filename=original_filename,
            file_path=file_path,
            file_hash_sha256=file_hash,
            file_size_bytes=file_size,
            total_pages=total_pages,
            mime_type="application/pdf",
            status="uploaded",
        )
        self.repo.create(new_document)

        # 9. Crear registro inicial de Job de procesamiento
        initial_job = ProcessingJob(
            document_id=new_document.id,
            stage="idle",
            progress_percent=0,
            total_chunks_indexed=0,
        )
        self.repo.create_job(initial_job)

        current_app.logger.info(
            f"Documento registrado: id={new_document.id}, "
            f"nombre='{original_filename}', páginas={total_pages}"
        )
        return new_document

    def get_document(self, document_id: str) -> Document:
        """Obtiene un documento por su ID o lanza DocumentNotFoundException."""
        try:
            doc_uuid = uuid.UUID(str(document_id))
        except ValueError:
            raise ValidationException("El identificador del documento no es un UUID válido.")

        document = self.repo.get_by_id(doc_uuid)
        if not document:
            raise DocumentNotFoundException(f"No se encontró el documento con ID: {document_id}")
        return document

    def list_documents(self, status: Optional[str] = None, search: Optional[str] = None) -> List[Document]:
        """Lista los documentos con filtros opcionales."""
        return self.repo.list_all(status=status, search=search)

    def delete_document(self, document_id: str) -> None:
        """Elimina el documento de PostgreSQL, borra sus vectores en ChromaDB y elimina el archivo físico."""
        document = self.get_document(document_id)

        # 1. Eliminar vectores en ChromaDB
        try:
            self.chroma.delete_by_document(str(document.id))
        except Exception as e:
            current_app.logger.warning(f"Aviso al eliminar vectores de ChromaDB para {document_id}: {str(e)}")

        # 2. Borrar archivo físico si existe
        if os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except OSError as e:
                current_app.logger.error(f"Error al eliminar archivo físico {document.file_path}: {str(e)}")

        # 3. Eliminar registro relacional en PostgreSQL
        self.repo.delete(document)
        current_app.logger.info(f"Documento y vectores eliminados exitosamente: id={document_id}")

    def trigger_indexing(self, document_id: str) -> ProcessingJob:
        """
        Ejecuta el pipeline completo de indexación RAG:
        Extracción por página (PyMuPDF/pdfplumber) -> Chunking consciente de tokens ->
        Generación de embeddings en Ollama -> Almacenamiento vectorial en ChromaDB ->
        Actualización de estado en PostgreSQL.
        """
        document = self.get_document(document_id)

        # 1. Actualizar estado a processing
        document.status = "processing"
        self.repo.update(document)

        job = ProcessingJob(
            document_id=document.id,
            stage="extracting",
            progress_percent=10,
            total_chunks_indexed=0,
        )
        self.repo.create_job(job)

        try:
            # 2. Extracción de páginas y tablas técnicas
            extracted_pages = PDFExtractor.extract_document(document.file_path)
            job.stage = "chunking"
            job.progress_percent = 30
            self.repo.update_job(job)

            # 3. Fragmentación semántica preservando número de página
            all_chunks = []
            # Limpiar secciones anteriores si es una reindexación
            DocumentSection.query.filter_by(document_id=document.id).delete()
            db.session.commit()

            for page in extracted_pages:
                page_chunks = self.text_splitter.split_page_into_chunks(
                    text=page.get_full_content(),
                    document_id=str(document.id),
                    filename=document.original_filename,
                    page_number=page.page_number,
                    has_tables=page.has_tables,
                )
                all_chunks.extend(page_chunks)

                # Registrar sección en PostgreSQL para trazabilidad estructural
                sec = DocumentSection(
                    document_id=document.id,
                    page_number=page.page_number,
                    chunks_count=len(page_chunks),
                    has_tables=page.has_tables,
                )
                db.session.add(sec)

            db.session.commit()

            if not all_chunks:
                raise AppException("No se generó ningún fragmento de texto a partir del documento.", status_code=422)

            # 4. Generación de embeddings con Ollama
            job.stage = "embedding"
            job.progress_percent = 50
            self.repo.update_job(job)

            embeddings = []
            total_chunks = len(all_chunks)
            for idx, ch in enumerate(all_chunks):
                emb = self.ollama.get_embedding(ch.content)
                embeddings.append(emb)

                # Actualizar progreso periódico
                if idx % 5 == 0 or idx == total_chunks - 1:
                    pct = 50 + int((idx + 1) / total_chunks * 40)
                    job.progress_percent = min(90, pct)
                    self.repo.update_job(job)

            # 5. Persistencia vectorial en ChromaDB
            job.stage = "indexing"
            job.progress_percent = 95
            self.repo.update_job(job)

            indexed_count = self.chroma.index_chunks(all_chunks, embeddings)

            # 6. Finalización exitosa
            job.stage = "completed"
            job.progress_percent = 100
            job.total_chunks_indexed = indexed_count
            job.finished_at = datetime.now(timezone.utc)
            self.repo.update_job(job)

            document.status = "indexed"
            document.total_pages = len(extracted_pages)
            self.repo.update(document)

            current_app.logger.info(
                f"Indexación exitosa para {document.original_filename}: "
                f"{len(extracted_pages)} páginas, {indexed_count} chunks almacenados en ChromaDB."
            )
            return job

        except Exception as e:
            # Captura de error y actualización de estado en PostgreSQL
            current_app.logger.exception(f"Fallo durante la indexación de {document.original_filename}: {str(e)}")
            job.stage = "failed"
            job.error_message = str(e)
            job.finished_at = datetime.now(timezone.utc)
            self.repo.update_job(job)

            document.status = "failed"
            self.repo.update(document)
            raise
