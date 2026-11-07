import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from flask import current_app
from src.core.exceptions import AppException
from src.services.text_splitter import Chunk


class ChromaService:
    """Servicio independiente de ChromaDB con persistencia local y colección para manuales técnicos."""

    COLLECTION_NAME = "industrial_manuals"

    def __init__(self, persist_directory: Optional[str] = None):
        self._persist_directory = persist_directory
        self._client = None
        self._collection = None

    @property
    def persist_directory(self) -> str:
        if self._persist_directory:
            return self._persist_directory
        if current_app:
            return current_app.config.get("CHROMA_PERSIST_DIRECTORY", "storage/chroma")
        return "storage/chroma"

    def _get_client(self) -> chromadb.PersistentClient:
        if self._client is None:
            os.makedirs(self.persist_directory, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )
        return self._client

    def get_or_create_collection(self) -> chromadb.Collection:
        """Obtiene o crea la colección con distancia coseno para similitud semántica."""
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine", "description": "Manuales técnicos industriales"},
            )
        return self._collection

    def index_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> int:
        """
        Inserta o actualiza fragmentos con sus vectores y metadatos (upsert).
        Valida que las dimensiones del vector coincidan.
        """
        if not chunks or not embeddings:
            return 0

        if len(chunks) != len(embeddings):
            raise AppException("La cantidad de chunks y vectores de embedding no coincide.", status_code=500)

        # 1. Comprobar dimensión real del primer vector
        first_dim = len(embeddings[0])
        if first_dim == 0:
            raise AppException("El vector de embedding tiene dimensión cero o está vacío.", status_code=500)

        collection = self.get_or_create_collection()

        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [c.to_metadata() for c in chunks]

        # Inserción atómica o por lotes (upsert previene duplicados en reindexación)
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        return len(ids)

    def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 4,
        document_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca los top_k fragmentos más cercanos mediante distancia coseno.
        Permite filtrar opcionalmente por un manual específico (document_id).
        """
        collection = self.get_or_create_collection()
        where_filter = {"document_id": str(document_id)} if document_id else None

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        formatted_results: List[Dict[str, Any]] = []

        if not results or not results.get("ids") or len(results["ids"][0]) == 0:
            return []

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for chunk_id, doc_text, meta, distance in zip(ids, documents, metadatas, distances):
            # En distancia coseno (0 a 2), la similitud se calcula como: 1 - (distancia / 2) o max(0, 1 - distancia)
            similarity = round(max(0.0, 1.0 - float(distance)), 4)
            formatted_results.append({
                "chunk_id": chunk_id,
                "document_id": meta.get("document_id"),
                "document_name": meta.get("filename"),
                "page_number": int(meta.get("page_number", 1)),
                "similarity_score": similarity,
                "distance": round(float(distance), 4),
                "content": doc_text,
                "is_table": meta.get("is_table", False),
            })

        return formatted_results

    def delete_by_document(self, document_id: str) -> None:
        """Elimina todos los fragmentos asociados a un manual en ChromaDB."""
        collection = self.get_or_create_collection()
        try:
            collection.delete(where={"document_id": str(document_id)})
        except Exception as e:
            current_app.logger.warning(f"Aviso al eliminar vectores del documento {document_id}: {str(e)}")

    def count_vectors(self) -> int:
        """Retorna el conteo total de fragmentos indexados en la colección."""
        collection = self.get_or_create_collection()
        return collection.count()
