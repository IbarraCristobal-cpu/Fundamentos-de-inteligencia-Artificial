"""Configuración central. Lee variables de entorno (y un archivo .env si existe)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")


@dataclass(frozen=True)
class Config:
    # --- Prolog ---
    swipl_path: str | None = os.getenv("SWIPL_PATH")
    prolog_script: Path = RAIZ / "prolog" / "una_pregunta.pl"
    prolog_timeout: float = float(os.getenv("PROLOG_TIMEOUT", "10"))

    # --- LLM ---
    # proveedor: "anthropic" | "openai" (cualquier API compatible: OpenAI, Ollama, Groq...)
    llm_provider: str = os.getenv("LLM_PROVIDER", "anthropic").lower()
    llm_model: str | None = os.getenv("LLM_MODEL")
    llm_api_key: str | None = os.getenv("LLM_API_KEY")
    llm_base_url: str | None = os.getenv("LLM_BASE_URL")
    llm_timeout: float = float(os.getenv("LLM_TIMEOUT", "60"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "500"))
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0"))
    conocimiento_path: Path = Path(os.getenv("CONOCIMIENTO_PATH", RAIZ / "conocimiento" / "transito.md"))

    # --- Web ---
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "5000"))
    max_chars_pregunta: int = 500


def cargar_config() -> Config:
    return Config()
