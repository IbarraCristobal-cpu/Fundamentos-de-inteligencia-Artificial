"""Chatbot #2: LLM que responde SOLO con el conocimiento recopilado.

Técnica: inyección del conocimiento en el prompt de sistema (el dominio es
pequeño, cabe completo en el contexto; no se necesita recuperación vectorial).
"""
from __future__ import annotations

import time

from .config import Config, cargar_config
from .knowledge import Conocimiento
from .llm_providers import LLMProvider, crear_proveedor
from .prolog_bot import RespuestaBot

INSTRUCCIONES = """Eres TransitoBot, un asistente del examen teórico de conducción de Chile.

REGLAS DE COMPORTAMIENTO
1. Responde ÚNICAMENTE con la base de conocimiento que aparece abajo. No uses conocimiento externo, aunque lo conozcas.
2. Si la pregunta se puede resolver aplicando las reglas de la base (por ejemplo, decidir si hay infracción comparando la velocidad con el límite), razona paso a paso con las reglas y da la conclusión.
3. Si la pregunta es de tránsito pero la base no contiene la información (multas, licencias, autopistas, otros vehículos, etc.), responde exactamente que eso no está en tu base de conocimiento y NO inventes ni estimes valores.
4. Si la pregunta no tiene relación con el tránsito, indica que solo puedes responder sobre el reglamento de tránsito.
5. Si falta un dato necesario (por ejemplo la zona al preguntar por una infracción), pídelo en lugar de suponerlo.
6. Responde en español, en 1 a 3 oraciones, e indica la regla aplicada (por ejemplo "Regla 2") cuando corresponda.

BASE DE CONOCIMIENTO
{conocimiento}
"""

MAX_TURNOS_HISTORIAL = 6  # mensajes previos que se reenvían al LLM


class LLMBot:
    nombre = "llm"

    def __init__(self, config: Config | None = None, proveedor: LLMProvider | None = None):
        self.config = config or cargar_config()
        self._proveedor = proveedor
        self._conocimiento = Conocimiento(self.config.conocimiento_path)

    @property
    def proveedor(self) -> LLMProvider:
        if self._proveedor is None:  # creación perezosa: permite arrancar la web sin API key
            self._proveedor = crear_proveedor(self.config)
        return self._proveedor

    def preguntar(self, texto: str, historial: list[dict] | None = None) -> RespuestaBot:
        sistema = INSTRUCCIONES.format(conocimiento=self._conocimiento.texto())
        mensajes = self._limpiar(historial) + [{"role": "user", "content": texto}]
        inicio = time.perf_counter()
        respuesta = self.proveedor.completar(sistema, mensajes)
        ms = int((time.perf_counter() - inicio) * 1000)
        return RespuestaBot(texto=respuesta, ms=ms, meta={"modelo": self.proveedor.modelo})

    @staticmethod
    def _limpiar(historial: list[dict] | None) -> list[dict]:
        """Conserva los últimos turnos válidos, alternando user/assistant.

        Devuelve una lista que empieza con "user" y termina con "assistant",
        para poder agregar a continuación el nuevo mensaje del usuario.
        """
        validos = [
            {"role": m["role"], "content": str(m["content"])[:1000]}
            for m in (historial or [])
            if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content")
        ][-MAX_TURNOS_HISTORIAL:]
        alternados: list[dict] = []
        for m in validos:
            esperado = "user" if not alternados or alternados[-1]["role"] == "assistant" else "assistant"
            if m["role"] == esperado:
                alternados.append(m)
        if alternados and alternados[-1]["role"] == "user":
            alternados.pop()
        return alternados
