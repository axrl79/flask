import time
from typing import List, Dict, Any, Optional
from flask import current_app
from src.services.ollama_service import OllamaService
from src.services.chroma_service import ChromaService
from src.core.exceptions import ValidationException, AppException


class RAGEngine:
    """Motor de consulta RAG fundamentado para documentación técnica industrial."""

    # Umbral de distancia coseno máxima admitida para considerar un fragmento relevante
    MAX_COSINE_DISTANCE_THRESHOLD = 0.68  # equivale a una similitud mínima >= 0.32

    SYSTEM_PROMPT = """Eres un asistente técnico industrial de alta precisión para personal de mantenimiento y planta.
Tu responsabilidad absoluta es responder preguntas operativas utilizando EXCLUSIVAMENTE los fragmentos de manuales técnicos provistos en el [CONTEXTO RECUPERADO].

REGLAS ESTRICTAS DE RESPUESTA:
1. Responde ÚNICAMENTE con los hechos, valores, pasos y especificaciones explícitas presentes en el contexto.
2. Si el contexto NO contiene información sobre la pregunta o la evidencia es insuficiente para responder con seguridad operativa, responde textualmente:
   "La documentación técnica disponible no contiene información suficiente para responder a esta consulta. Por favor, verifique el manual oficial del fabricante o consulte con el supervisor de mantenimiento antes de intervenir el equipo."
3. NUNCA inventes, deduzcas ni extrapoles códigos de error, presiones, torques de apriete, lubricantes, secuencias de desmontaje ni parámetros eléctricos.
4. En cada procedimiento, dato numérico o especificación que menciones, DEBES citar la fuente exacta al final de la oración usando el formato: [Manual: <nombre_manual>, Pág. <numero_pagina>].
5. Mantén un tono técnico, formal, conciso y orientado a la seguridad industrial."""

    def __init__(self, ollama_service: Optional[OllamaService] = None, chroma_service: Optional[ChromaService] = None):
        self.ollama = ollama_service or OllamaService()
        self.chroma = chroma_service or ChromaService()

    def query(
        self,
        question: str,
        document_id: Optional[str] = None,
        top_k: int = 4,
    ) -> Dict[str, Any]:
        """
        Ejecuta el ciclo completo de consulta RAG:
        Pregunta -> Embedding -> Búsqueda semántica -> Filtro de relevancia -> Contexto -> Inferencia -> Citas.
        """
        if not question or not question.strip():
            raise ValidationException("La pregunta no puede estar vacía.")

        clean_question = question.strip()
        start_time = time.time()

        # 1. Generar embedding de la pregunta con Ollama
        query_vector = self.ollama.get_embedding(clean_question)

        # 2. Búsqueda vectorial en ChromaDB con filtrado opcional por documento
        raw_chunks = self.chroma.search_similar(
            query_embedding=query_vector,
            top_k=max(2, min(top_k, 8)),
            document_id=document_id,
        )

        # 3. Filtrar por umbral de relevancia semántica
        relevant_chunks = [
            c for c in raw_chunks
            if c.get("distance", 1.0) <= self.MAX_COSINE_DISTANCE_THRESHOLD
        ]

        # 4. Control de evidencia insuficiente
        if not relevant_chunks:
            latency = round(time.time() - start_time, 2)
            return {
                "answer": (
                    "No se encontró información relevante en los manuales técnicos para responder a esta consulta. "
                    "Asegúrese de que el manual correspondiente esté indexado o reformule la pregunta con términos técnicos específicos."
                ),
                "sources": [],
                "evidence_sufficient": False,
                "model_used": current_app.config.get("OLLAMA_LLM_MODEL", "llama3.1:8b"),
                "latency_seconds": latency,
            }

        # 5. Construcción del contexto ordenado y acotado
        context_parts = []
        sources = []

        for c in relevant_chunks:
            source_ref = f"[Manual: {c['document_name']}, Pág. {c['page_number']}]"
            context_parts.append(f"--- INICIO FRAGMENTO {source_ref} ---\n{c['content']}\n--- FIN FRAGMENTO ---")

            # Extracto corto para la tarjeta de referencia en el frontend
            snippet = c["content"]
            # Remover encabezado de inyección si está presente
            if snippet.startswith("[Manual:"):
                snippet = snippet.split("\n", 1)[-1]
            snippet_preview = snippet.strip()[:240] + ("..." if len(snippet.strip()) > 240 else "")

            sources.append({
                "chunk_id": c["chunk_id"],
                "document_id": c["document_id"],
                "document_name": c["document_name"],
                "page_number": c["page_number"],
                "similarity_score": c["similarity_score"],
                "snippet": snippet_preview,
                "is_table": c.get("is_table", False),
            })

        context_str = "\n\n".join(context_parts)

        user_prompt = f"""[CONTEXTO RECUPERADO DE MANUALES TÉCNICOS]
{context_str}

[PREGUNTA DEL TÉCNICO]
{clean_question}

[RESPUESTA TÉCNICA FUNDAMENTADA]:"""

        # 6. Generar respuesta con Ollama (temperatura = 0.0)
        generation_result = self.ollama.generate(
            prompt=user_prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.0,
        )

        total_latency = round(time.time() - start_time, 2)

        return {
            "answer": generation_result["response"],
            "sources": sources,
            "evidence_sufficient": True,
            "model_used": generation_result["model"],
            "latency_seconds": total_latency,
        }
