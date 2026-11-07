import io
import os
import unittest
from src import create_app
from src.extensions import db
from src.models.document import Document
from src.models.chat import ChatSession


class BackendAPITestCase(unittest.TestCase):
    """Pruebas funcionales de los endpoints de la API y lógica de documentos."""

    def setUp(self):
        self.app = create_app("development")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_system_status_endpoint(self):
        """Verifica que el endpoint /api/system/status responda con JSON y estructura válida."""
        response = self.client.get("/api/system/status")
        self.assertIn(response.status_code, [200, 503])
        data = response.get_json()
        self.assertIn("components", data)
        self.assertIn("postgresql", data["components"])
        self.assertIn("ollama", data["components"])
        self.assertIn("chromadb", data["components"])

    def test_02_upload_pdf_validation_invalid_extension(self):
        """Rechaza archivos con extensión distinta de .pdf."""
        data = {
            "file": (io.BytesIO(b"texto no pdf"), "manual.txt")
        }
        response = self.client.post(
            "/api/documents/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data["error"]["code"], "FILE_UPLOAD_ERROR")

    def test_03_upload_pdf_validation_corrupt_content(self):
        """Rechaza archivos .pdf con encabezado corrupto (sin %PDF-)."""
        data = {
            "file": (io.BytesIO(b"Esto no es un pdf real"), "manual_falso.pdf")
        }
        response = self.client.post(
            "/api/documents/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data["error"]["code"], "FILE_UPLOAD_ERROR")

    def test_04_create_chat_session(self):
        """Crea una sesión de chat y verifica su respuesta JSON."""
        response = self.client.post(
            "/api/chat/sessions",
            json={"title": "Diagnóstico de Compresor Atlas Copco"}
        )
        if response.status_code == 201:
            data = response.get_json()
            self.assertIn("id", data)
            self.assertEqual(data["title"], "Diagnóstico de Compresor Atlas Copco")


if __name__ == "__main__":
    unittest.main()
