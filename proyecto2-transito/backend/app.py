"""API web (Flask) + frontend estático.

Endpoints:
  GET  /               -> interfaz web
  GET  /api/estado     -> disponibilidad de cada chatbot
  POST /api/chat       -> {"pregunta": str, "modo": "prolog"|"llm"|"ambos", "historial": [...]}
"""
from __future__ import annotations

import logging

from flask import Flask, jsonify, request, send_from_directory

from .config import RAIZ, Config, cargar_config
from .llm_bot import LLMBot
from .llm_providers import LLMError
from .prolog_bot import PrologBot, PrologNoDisponible

log = logging.getLogger("transitobot")
MODOS = ("prolog", "llm", "ambos")


def crear_app(config: Config | None = None, prolog_bot=None, llm_bot=None) -> Flask:
    config = config or cargar_config()
    prolog_bot = prolog_bot or PrologBot(config)
    llm_bot = llm_bot or LLMBot(config)

    app = Flask(__name__, static_folder=str(RAIZ / "frontend"), static_url_path="/static")

    @app.get("/")
    def inicio():
        return send_from_directory(RAIZ / "frontend", "index.html")

    @app.get("/api/estado")
    def estado():
        return jsonify({"prolog": _ok(lambda: prolog_bot.preguntar("hola")),
                        "llm": _ok(lambda: llm_bot.proveedor and True)})

    @app.post("/api/chat")
    def chat():
        datos = request.get_json(silent=True) or {}
        pregunta = str(datos.get("pregunta", "")).strip()
        modo = datos.get("modo", "ambos")
        if not pregunta:
            return jsonify({"error": "Escribe una pregunta."}), 400
        if len(pregunta) > config.max_chars_pregunta:
            return jsonify({"error": f"La pregunta supera {config.max_chars_pregunta} caracteres."}), 400
        if modo not in MODOS:
            return jsonify({"error": f"Modo inválido. Usa: {', '.join(MODOS)}."}), 400

        resultado = {}
        if modo in ("prolog", "ambos"):
            resultado["prolog"] = _ejecutar(lambda: prolog_bot.preguntar(pregunta), (PrologNoDisponible,))
        if modo in ("llm", "ambos"):
            historial = datos.get("historial") if isinstance(datos.get("historial"), list) else None
            resultado["llm"] = _ejecutar(lambda: llm_bot.preguntar(pregunta, historial), (LLMError,))
        return jsonify(resultado)

    return app


def _ejecutar(fn, errores_esperados):
    """Corre un chatbot y devuelve siempre un dict serializable (nunca lanza)."""
    try:
        r = fn()
        return {"ok": True, "respuesta": r.texto, "ms": r.ms, **r.meta}
    except errores_esperados as exc:
        return {"ok": False, "error": str(exc)}
    except Exception:  # noqa: BLE001 - la web no debe caerse por un chatbot
        log.exception("Error inesperado en un chatbot")
        return {"ok": False, "error": "Error interno inesperado."}


def _ok(fn) -> dict:
    try:
        fn()
        return {"disponible": True}
    except Exception as exc:  # noqa: BLE001
        return {"disponible": False, "motivo": str(exc)}


def main():
    config = cargar_config()
    app = crear_app(config)
    print(f"TransitoBot en http://{config.host}:{config.port}")
    app.run(host=config.host, port=config.port, debug=False)


if __name__ == "__main__":
    main()
