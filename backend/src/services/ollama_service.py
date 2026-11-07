import json
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from flask import current_app
from src.core.exceptions import ServiceUnavailableException, AppException


class OllamaService:
    """Cliente HTTP desacoplado para inferencia y generación de embeddings con Ollama local."""

    def __init__(self, base_url: Optional[str] = None):
        self._base_url = base_url

    @property
    def base_url(self) -> str:
        if self._base_url:
            return self._base_url
        if current_app:
            return current_app.config.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        return "http://127.0.0.1:11434"

    def is_service_online(self) -> bool:
        """Verifica si el demonio de Ollama está accesible en la URL configurada."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

    def list_available_models(self) -> List[str]:
        """Obtiene la lista de nombres de modelos descargados localmente en Ollama."""
        url = f"{self.base_url}/api/tags"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "RAG-Flask-OllamaClient"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return [m.get("name") for m in data.get("models", [])]
                return []
        except urllib.error.URLError as e:
            raise ServiceUnavailableException(
                f"No se pudo conectar con el servicio local de Ollama en {self.base_url}. Verifique que el servicio esté activo.",
                details={"error": str(e)},
            )

    def is_model_available(self, model_name: str) -> bool:
        """Comprueba si un modelo o familia de modelo está disponible en Ollama."""
        models = self.list_available_models()
        # Verificar coincidencia exacta o con prefijo (ej: nomic-embed-text o nomic-embed-text:latest)
        target = model_name.split(":")[0]
        return any(m.split(":")[0] == target for m in models)

    def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Genera el vector de embedding para un texto dado.
        Usa /api/embed (moderno) o /api/embeddings (legacy).
        """
        default_model = "nomic-embed-text"
        try:
            if current_app:
                default_model = current_app.config.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        except RuntimeError:
            pass
        model_name = model or default_model

        # Comprobar disponibilidad del modelo sin descargarlo automáticamente
        if not self.is_model_available(model_name):
            available = self.list_available_models()
            raise AppException(
                f"El modelo de embeddings '{model_name}' no está instalado en Ollama local. "
                f"Modelos disponibles actualmente: {available}. "
                "Para descargarlo, ejecute manualmente: ollama pull nomic-embed-text",
                status_code=503,
                details={"required_model": model_name, "available_models": available},
            )

        # 1. Intentar con /api/embed (Ollama >= 0.1.30)
        embed_url = f"{self.base_url}/api/embed"
        payload = json.dumps({"model": model_name, "input": text}).encode("utf-8")
        req = urllib.request.Request(
            embed_url,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "RAG-Flask"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    result = json.loads(resp.read().decode("utf-8"))
                    embeddings = result.get("embeddings")
                    if embeddings and len(embeddings) > 0:
                        return embeddings[0]
        except urllib.error.HTTPError as he:
            # Fallback a /api/embeddings
            legacy_url = f"{self.base_url}/api/embeddings"
            legacy_payload = json.dumps({"model": model_name, "prompt": text}).encode("utf-8")
            legacy_req = urllib.request.Request(
                legacy_url,
                data=legacy_payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(legacy_req, timeout=30) as l_resp:
                    if l_resp.status == 200:
                        l_result = json.loads(l_resp.read().decode("utf-8"))
                        return l_result.get("embedding", [])
            except Exception as e:
                raise AppException(
                    f"Fallo al generar embedding con Ollama: {str(e)}",
                    status_code=500,
                )
        except Exception as e:
            raise AppException(f"Error comunicando con Ollama embeddings: {str(e)}", status_code=500)

        raise AppException("Ollama no devolvió ningún vector de embedding.", status_code=500)

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Ejecuta la inferencia LLM en Ollama con temperatura determinista (0.0).
        """
        default_model = "llama3.1:8b"
        try:
            if current_app:
                default_model = current_app.config.get("OLLAMA_LLM_MODEL", "llama3.1:8b")
        except RuntimeError:
            pass
        model_name = model or default_model

        # Comprobar si el modelo está instalado; si no, buscar alternativa instalada si existe
        if not self.is_model_available(model_name):
            available = self.list_available_models()
            # Si llama3.1:8b aún se está descargando pero llama3.2:1b o mistral está disponible, usarlo como fallback
            fallback_models = [m for m in available if not m.startswith("nomic-embed")]
            if fallback_models:
                fallback_name = fallback_models[0]
                current_app.logger.info(f"Modelo {model_name} no listo. Usando fallback disponible: {fallback_name}")
                model_name = fallback_name
            else:
                raise AppException(
                    f"El modelo LLM configurado '{model_name}' no está disponible aún en Ollama. "
                    f"Modelos disponibles: {available}. "
                    "Descargue el modelo con: ollama pull llama3.1:8b",
                    status_code=503,
                    details={"required_model": model_name, "available_models": available},
                )

        start_time = time.time()
        url = f"{self.base_url}/api/generate"
        payload = json.dumps({
            "model": model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.1,
                "repeat_penalty": 1.15,
            },
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "RAG-Flask"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                latency = round(time.time() - start_time, 2)
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return {
                        "response": data.get("response", "").strip(),
                        "model": model_name,
                        "latency_seconds": latency,
                        "eval_count": data.get("eval_count"),
                    }
                raise AppException(f"Respuesta inesperada de Ollama: status {resp.status}", status_code=500)
        except urllib.error.URLError as e:
            raise ServiceUnavailableException(
                f"Ollama no respondió durante la inferencia: {str(e)}",
                details={"error": str(e)},
            )
