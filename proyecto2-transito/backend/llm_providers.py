"""Proveedores de LLM intercambiables. Solo usan `requests` (sin SDKs).

- AnthropicProvider      -> API de Claude (/v1/messages)
- OpenAICompatibleProvider -> OpenAI, Ollama (local y gratis), Groq, etc. (/chat/completions)
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod

import requests

from .config import Config


class LLMError(RuntimeError):
    """Fallo al consultar el LLM (credenciales, red, límite de uso...)."""


class LLMProvider(ABC):
    modelo: str

    @abstractmethod
    def completar(self, sistema: str, mensajes: list[dict]) -> str:
        """`mensajes`: [{"role": "user"|"assistant", "content": str}, ...]"""


def _post(url: str, headers: dict, payload: dict, timeout: float) -> dict:
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise LLMError(f"No se pudo conectar con el LLM: {exc}") from exc
    if r.status_code != 200:
        raise LLMError(f"El LLM respondió HTTP {r.status_code}: {r.text[:300]}")
    try:
        return r.json()
    except ValueError as exc:
        raise LLMError("La respuesta del LLM no es JSON válido.") from exc


class AnthropicProvider(LLMProvider):
    def __init__(self, config: Config):
        self.api_key = config.llm_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise LLMError("Falta la API key: define LLM_API_KEY (o ANTHROPIC_API_KEY) en .env")
        self.modelo = config.llm_model or "claude-haiku-5-5"
        self.base_url = (config.llm_base_url or "https://api.anthropic.com").rstrip("/")
        self.config = config

    def completar(self, sistema: str, mensajes: list[dict]) -> str:
        datos = _post(
            f"{self.base_url}/v1/messages",
            {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            {
                "model": self.modelo,
                "max_tokens": self.config.llm_max_tokens,
                "temperature": self.config.llm_temperature,
                "system": sistema,
                "messages": mensajes,
            },
            self.config.llm_timeout,
        )
        partes = [b.get("text", "") for b in datos.get("content", []) if b.get("type") == "text"]
        texto = "".join(partes).strip()
        if not texto:
            raise LLMError("El LLM devolvió una respuesta vacía.")
        return texto


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, config: Config):
        self.base_url = (config.llm_base_url or "https://api.openai.com/v1").rstrip("/")
        self.api_key = config.llm_api_key or os.getenv("OPENAI_API_KEY")
        es_local = "localhost" in self.base_url or "127.0.0.1" in self.base_url
        if not self.api_key and not es_local:
            raise LLMError("Falta la API key: define LLM_API_KEY en .env")
        self.modelo = config.llm_model or ("llama3.1" if es_local else "gpt-4o-mini")
        self.config = config

    def completar(self, sistema: str, mensajes: list[dict]) -> str:
        headers = {"content-type": "application/json"}
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        datos = _post(
            f"{self.base_url}/chat/completions",
            headers,
            {
                "model": self.modelo,
                "max_tokens": self.config.llm_max_tokens,
                "temperature": self.config.llm_temperature,
                "messages": [{"role": "system", "content": sistema}, *mensajes],
            },
            self.config.llm_timeout,
        )
        try:
            texto = datos["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError) as exc:
            raise LLMError("Formato de respuesta inesperado del LLM.") from exc
        if not texto:
            raise LLMError("El LLM devolvió una respuesta vacía.")
        return texto


def crear_proveedor(config: Config) -> LLMProvider:
    if config.llm_provider == "anthropic":
        return AnthropicProvider(config)
    if config.llm_provider in ("openai", "ollama"):
        return OpenAICompatibleProvider(config)
    raise LLMError(f"Proveedor desconocido: {config.llm_provider!r} (usa 'anthropic' u 'openai')")
