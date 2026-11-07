import os
import unittest
import pymupdf
from src import create_app
from src.services.pdf_extractor import PDFExtractor, ExtractedPage
from src.services.text_splitter import TokenAwareTextSplitter
from src.services.chroma_service import ChromaService
from src.services.ollama_service import OllamaService
from src.services.rag_engine import RAGEngine
from src.core.exceptions import AppException
from tests.create_sample_pdf import create_sample_industrial_manual


class RAGPipelineTestCase(unittest.TestCase):
    """Pruebas exhaustivas del núcleo RAG, extracción de PDF, chunking y base vectorial."""

    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.pdf_path = os.path.join(base_dir, "test_ga37_manual.pdf")
        create_sample_industrial_manual(cls.pdf_path)

        # Crear PDF vacío/escaneado sin texto para probar detección de OCR
        cls.empty_pdf_path = os.path.join(base_dir, "test_scanned_empty.pdf")
        empty_doc = pymupdf.open()
        empty_doc.new_page()  # Página en blanco sin texto
        empty_doc.save(cls.empty_pdf_path)
        empty_doc.close()

    @classmethod
    def tearDownClass(cls):
        for p in [cls.pdf_path, cls.empty_pdf_path]:
            if os.path.exists(p):
                os.remove(p)

    def setUp(self):
        self.app = create_app("development")
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_pdf_extractor_success(self):
        """Verifica la extracción de páginas, texto y metadatos de un manual técnico."""
        pages = PDFExtractor.extract_document(self.pdf_path)
        self.assertEqual(len(pages), 4)
        self.assertEqual(pages[0].page_number, 1)
        self.assertIn("PROCEDIMIENTO DE ARRANQUE", pages[0].text)
        self.assertIn("10.5 bar", pages[1].text)
        self.assertIn("Código E-205", pages[2].text)
        self.assertIn("4000 horas", pages[3].text)

    def test_02_pdf_extractor_detects_scanned_ocr_required(self):
        """Detecta si un PDF carece de texto digital y exige OCR sin inventar contenido."""
        with self.assertRaises(AppException) as ctx:
            PDFExtractor.extract_document(self.empty_pdf_path)
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertTrue(ctx.exception.details.get("requires_ocr"))

    def test_03_token_aware_text_splitter(self):
        """Comprueba que los fragmentos respeten tamaño de tokens, solapamiento y cabeceras de procedencia."""
        splitter = TokenAwareTextSplitter(target_chunk_tokens=550, overlap_tokens=90)
        pages = PDFExtractor.extract_document(self.pdf_path)

        chunks = []
        for p in pages:
            ch_list = splitter.split_page_into_chunks(
                text=p.get_full_content(),
                document_id="doc-test-123",
                filename="Manual_GA37.pdf",
                page_number=p.page_number,
                has_tables=p.has_tables,
            )
            chunks.extend(ch_list)

        self.assertGreater(len(chunks), 0)
        for ch in chunks:
            self.assertTrue(ch.content.startswith("[Manual: Manual_GA37.pdf | Pág."))
            self.assertGreater(ch.token_count, 10)
            self.assertLess(ch.token_count, 650)
            self.assertTrue(ch.chunk_id.startswith("doc-test-123_p"))

    def test_04_chroma_service_indexing_and_search(self):
        """Verifica la persistencia, indexación vectorial, similitud y eliminación en ChromaDB."""
        chroma = ChromaService(persist_directory="storage/chroma_test")
        splitter = TokenAwareTextSplitter(target_chunk_tokens=300, overlap_tokens=50)
        pages = PDFExtractor.extract_document(self.pdf_path)

        chunks = []
        for p in pages:
            ch_list = splitter.split_page_into_chunks(
                text=p.get_full_content(),
                document_id="ga37-uuid-test",
                filename="GA37_Manual.pdf",
                page_number=p.page_number,
                has_tables=p.has_tables,
            )
            chunks.extend(ch_list)

        # Simular vectores densos de 768 dimensiones (dimensión de nomic-embed-text)
        import random
        random.seed(42)
        embeddings = [[random.uniform(-0.1, 0.1) for _ in range(768)] for _ in chunks]

        # Indexar
        count = chroma.index_chunks(chunks, embeddings)
        self.assertEqual(count, len(chunks))

        # Consultar con vector idéntico al primero para verificar recuperación por coseno
        query_vec = embeddings[0]
        results = chroma.search_similar(query_vec, top_k=2, document_id="ga37-uuid-test")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["document_id"], "ga37-uuid-test")
        self.assertGreaterEqual(results[0]["similarity_score"], 0.95)

        # Probar eliminación por documento
        chroma.delete_by_document("ga37-uuid-test")
        results_after_delete = chroma.search_similar(query_vec, top_k=2, document_id="ga37-uuid-test")
        self.assertEqual(len(results_after_delete), 0)

    def test_05_ollama_service_model_check(self):
        """Verifica la inspección de modelos de Ollama y el reporte de modelos faltantes."""
        ollama = OllamaService()
        self.assertTrue(ollama.is_service_online())
        available = ollama.list_available_models()
        self.assertIsInstance(available, list)
        self.assertTrue(any("llama3.2:1b" in m for m in available))

        # Intentar pedir embedding sin modelo descargado debe arrojar AppException con código 503
        with self.assertRaises(AppException) as ctx:
            ollama.get_embedding("texto de prueba", model="modelo_inexistente_123")
        self.assertEqual(ctx.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
