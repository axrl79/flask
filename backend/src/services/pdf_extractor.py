import os
import re
from typing import List, Dict, Any, Tuple
import pymupdf  # PyMuPDF
import pdfplumber
from flask import current_app
from src.core.exceptions import ValidationException, AppException


class ExtractedPage:
    def __init__(self, page_number: int, text: str, has_tables: bool = False, tables_markdown: str = ""):
        self.page_number = page_number
        self.text = text
        self.has_tables = has_tables
        self.tables_markdown = tables_markdown

    def get_full_content(self) -> str:
        """Combina el texto principal con las tablas en Markdown de forma coherente."""
        parts = []
        if self.text.strip():
            parts.append(self.text.strip())
        if self.tables_markdown.strip():
            parts.append("\n### Tablas y Especificaciones Técnicas:\n" + self.tables_markdown.strip())
        return "\n\n".join(parts)


class PDFExtractor:
    """Extractor especializado de texto y tablas técnicas por página."""

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """Limpia caracteres nulos, secuencias de control y espacios en blanco excesivos."""
        if not raw_text:
            return ""
        # Eliminar caracteres nulos
        text = raw_text.replace("\x00", "")
        # Normalizar saltos de línea y tabulaciones múltiples
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        return text.strip()

    @staticmethod
    def table_to_markdown(table: List[List[Any]]) -> str:
        """Convierte una matriz 2D de pdfplumber a una tabla Markdown estructurada."""
        if not table or len(table) < 2:
            return ""

        # Limpiar celdas vacías y saltos internos
        cleaned_table = []
        for row in table:
            cleaned_row = [
                str(cell).replace("\n", " ").strip() if cell is not None else ""
                for cell in row
            ]
            if any(cleaned_row):  # Si la fila tiene al menos una celda no vacía
                cleaned_table.append(cleaned_row)

        if len(cleaned_table) < 2:
            return ""

        headers = cleaned_table[0]
        # Si las cabeceras están vacías, asignar Columna 1, Columna 2...
        headers = [h if h else f"Columna {idx+1}" for idx, h in enumerate(headers)]
        separator = ["---"] * len(headers)

        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(separator) + " |",
        ]

        for row in cleaned_table[1:]:
            # Ajustar longitud de fila a la cabecera
            adjusted_row = row[:len(headers)] + [""] * max(0, len(headers) - len(row))
            lines.append("| " + " | ".join(adjusted_row) + " |")

        return "\n".join(lines)

    @classmethod
    def extract_tables_with_pdfplumber(cls, file_path: str, page_number: int) -> Tuple[bool, str]:
        """Extrae tablas de una página específica con pdfplumber y las convierte a Markdown."""
        try:
            with pdfplumber.open(file_path) as pdf:
                if page_number > len(pdf.pages):
                    return False, ""
                page = pdf.pages[page_number - 1]
                tables = page.extract_tables()
                if not tables:
                    return False, ""

                md_tables = []
                for t in tables:
                    md = cls.table_to_markdown(t)
                    if md:
                        md_tables.append(md)

                if md_tables:
                    return True, "\n\n".join(md_tables)
                return False, ""
        except Exception as e:
            current_app.logger.warning(f"Advertencia en pdfplumber pág {page_number}: {str(e)}")
            return False, ""

    @classmethod
    def extract_document(cls, file_path: str) -> List[ExtractedPage]:
        """
        Extrae y normaliza el contenido del documento PDF página por página.
        Detecta si el documento está escaneado (sin texto) y genera advertencia de OCR.
        """
        if not os.path.exists(file_path):
            raise ValidationException(f"El archivo '{file_path}' no existe en disco.")

        pages_extracted: List[ExtractedPage] = []
        total_text_length = 0

        try:
            with pymupdf.open(file_path) as doc:
                total_pages = doc.page_count
                if total_pages == 0:
                    raise ValidationException("El archivo PDF está vacío o no tiene páginas válidas.")

                for page_idx in range(total_pages):
                    page_num = page_idx + 1
                    fitz_page = doc[page_idx]

                    # 1. Extracción de texto base con PyMuPDF (muy rápido y respeta bloques)
                    raw_text = fitz_page.get_text("text") or ""
                    cleaned_text = cls.clean_text(raw_text)
                    total_text_length += len(cleaned_text)

                    # 2. Extracción de tablas complementaria si hay indicios tabulares o de especificaciones
                    has_tables, tables_md = False, ""
                    # Buscar líneas con posibles tablas (múltiples números, separadores o palabras clave)
                    if any(term in cleaned_text.lower() for term in ["tabla", "especificaciones", "torque", "par", "bar", "kw", "dimensión", "código"]):
                        has_tables, tables_md = cls.extract_tables_with_pdfplumber(file_path, page_num)

                    pages_extracted.append(
                        ExtractedPage(
                            page_number=page_num,
                            text=cleaned_text,
                            has_tables=has_tables,
                            tables_markdown=tables_md,
                        )
                    )

        except Exception as e:
            if isinstance(e, ValidationException):
                raise
            raise AppException(f"Error procesando el archivo PDF con PyMuPDF: {str(e)}", status_code=500)

        # 3. Verificación de documento escaneado (sin texto extraíble)
        if total_text_length < 20 and total_pages > 0:
            raise AppException(
                "El documento no contiene texto digital extraíble (probablemente es un PDF escaneado con imágenes). "
                "Se requiere un proceso de OCR previo para poder indexar este archivo.",
                status_code=422,
                details={"total_pages": total_pages, "characters_extracted": total_text_length, "requires_ocr": True},
            )

        return pages_extracted
