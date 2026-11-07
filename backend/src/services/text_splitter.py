import re
from typing import List, Dict, Any


class Chunk:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        filename: str,
        page_number: int,
        chunk_index: int,
        content: str,
        token_count: int,
        is_table: bool = False,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.filename = filename
        self.page_number = page_number
        self.chunk_index = chunk_index
        self.content = content
        self.token_count = token_count
        self.is_table = is_table

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": str(self.document_id),
            "filename": self.filename,
            "page_number": int(self.page_number),
            "chunk_index": int(self.chunk_index),
            "token_count": int(self.token_count),
            "is_table": bool(self.is_table),
        }


class TokenAwareTextSplitter:
    """
    Divisor semántico de texto consciente de tokens.
    Distingue caracteres, palabras y tokens (BPE subword estimation con ratio 3.8 car/tok en español técnico).
    Preserva tablas completas en la medida de lo posible y aplica solapamiento.
    """

    def __init__(self, target_chunk_tokens: int = 550, overlap_tokens: int = 90):
        self.target_tokens = target_chunk_tokens
        self.overlap_tokens = overlap_tokens
        # Calibración media: ~3.8 caracteres por token en español técnico con números y códigos
        self.chars_per_token = 3.8
        self.max_chars = int(self.target_tokens * self.chars_per_token)
        self.overlap_chars = int(self.overlap_tokens * self.chars_per_token)

    def estimate_tokens(self, text: str) -> int:
        """Calcula el número de tokens aproximado mediante conteo subpalabra ponderado."""
        if not text:
            return 0
        # Cuenta palabras, puntuación y caracteres técnicos por separado
        words = len(re.findall(r"\w+", text))
        punctuation = len(re.findall(r"[^\w\s]", text))
        # En vocabularios técnicos Llama/Mistral, símbolos y números añaden tokens adicionales
        estimated = int((len(text) / self.chars_per_token + words + punctuation * 0.5) / 2)
        return max(1, estimated)

    def split_page_into_chunks(
        self,
        text: str,
        document_id: str,
        filename: str,
        page_number: int,
        has_tables: bool = False,
    ) -> List[Chunk]:
        """
        Fragmenta el texto de una página respetando párrafos, encabezados y tablas.
        Inyecta encabezado de contexto: [Manual: {filename} | Pág. {page_number}]
        """
        if not text or not text.strip():
            return []

        chunks: List[Chunk] = []
        header = f"[Manual: {filename} | Pág. {page_number}]\n"
        header_tokens = self.estimate_tokens(header)
        effective_max_chars = self.max_chars - len(header)
        effective_overlap_chars = self.overlap_chars

        # Separadores jerárquicos: secciones Markdown, párrafos dobles, oraciones, saltos simples
        paragraphs = text.split("\n\n")
        current_chunk_parts: List[str] = []
        current_length = 0
        chunk_idx = 1

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_len = len(para)

            # Si el párrafo por sí solo excede el límite (ej. tabla muy grande o bloque extenso)
            if para_len > effective_max_chars:
                # Si teníamos partes acumuladas, vaciar el chunk actual primero
                if current_chunk_parts:
                    chunk_text = header + "\n\n".join(current_chunk_parts)
                    chunks.append(
                        Chunk(
                            chunk_id=f"{document_id}_p{page_number}_c{chunk_idx}",
                            document_id=document_id,
                            filename=filename,
                            page_number=page_number,
                            chunk_index=chunk_idx,
                            content=chunk_text,
                            token_count=self.estimate_tokens(chunk_text),
                            is_table=has_tables and "|" in chunk_text,
                        )
                    )
                    chunk_idx += 1
                    current_chunk_parts = []
                    current_length = 0

                # Dividir el párrafo grande por oraciones
                sentences = re.split(r"(?<=[.!?]) +", para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    if current_length + len(sentence) > effective_max_chars and current_chunk_parts:
                        chunk_text = header + " ".join(current_chunk_parts)
                        chunks.append(
                            Chunk(
                                chunk_id=f"{document_id}_p{page_number}_c{chunk_idx}",
                                document_id=document_id,
                                filename=filename,
                                page_number=page_number,
                                chunk_index=chunk_idx,
                                content=chunk_text,
                                token_count=self.estimate_tokens(chunk_text),
                                is_table=has_tables and "|" in chunk_text,
                            )
                        )
                        chunk_idx += 1
                        # Mantener solapamiento de las últimas oraciones
                        overlap_parts = []
                        overlap_len = 0
                        for p in reversed(current_chunk_parts):
                            if overlap_len + len(p) <= effective_overlap_chars:
                                overlap_parts.insert(0, p)
                                overlap_len += len(p)
                            else:
                                break
                        current_chunk_parts = overlap_parts
                        current_length = overlap_len

                    current_chunk_parts.append(sentence)
                    current_length += len(sentence)
            else:
                # Comprobar si añadir el párrafo supera el tamaño objetivo
                if current_length + para_len > effective_max_chars and current_chunk_parts:
                    chunk_text = header + "\n\n".join(current_chunk_parts)
                    chunks.append(
                        Chunk(
                            chunk_id=f"{document_id}_p{page_number}_c{chunk_idx}",
                            document_id=document_id,
                            filename=filename,
                            page_number=page_number,
                            chunk_index=chunk_idx,
                            content=chunk_text,
                            token_count=self.estimate_tokens(chunk_text),
                            is_table=has_tables and "|" in chunk_text,
                        )
                    )
                    chunk_idx += 1

                    # Solapamiento: conservar el último párrafo si cabe dentro del límite de overlap
                    if len(current_chunk_parts[-1]) <= effective_overlap_chars:
                        current_chunk_parts = [current_chunk_parts[-1]]
                        current_length = len(current_chunk_parts[0])
                    else:
                        current_chunk_parts = []
                        current_length = 0

                current_chunk_parts.append(para)
                current_length += para_len

        # Último chunk remanente
        if current_chunk_parts:
            chunk_text = header + "\n\n".join(current_chunk_parts)
            chunks.append(
                Chunk(
                    chunk_id=f"{document_id}_p{page_number}_c{chunk_idx}",
                    document_id=document_id,
                    filename=filename,
                    page_number=page_number,
                    chunk_index=chunk_idx,
                    content=chunk_text,
                    token_count=self.estimate_tokens(chunk_text),
                    is_table=has_tables and "|" in chunk_text,
                )
            )

        return chunks
