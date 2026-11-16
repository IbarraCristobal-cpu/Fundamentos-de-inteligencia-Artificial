import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from backend.config import Config
from backend.llm_bot import LLMBot
from backend.llm_providers import AnthropicProvider, LLMError, OpenAICompatibleProvider, crear_proveedor


class Falso:
    """Proveedor de prueba: registra lo que recibe."""
    modelo = "falso"

    def __init__(self):
        self.sistema = None
        self.mensajes = None

    def completar(self, sistema, mensajes):
        self.sistema, self.mensajes = sistema, mensajes
        return "respuesta de prueba"


def test_prompt_incluye_el_conocimiento():
    f = Falso()
    LLMBot(proveedor=f).preguntar("¿Límite urbano?")
    assert "50 km/h" in f.sistema and "BASE DE CONOCIMIENTO" in f.sistema
    assert f.mensajes == [{"role": "user", "content": "¿Límite urbano?"}]


def test_historial_se_limpia_y_alterna():
    f = Falso()
    historial = [
        {"role": "assistant", "content": "huérfano"},          # no puede abrir la conversación
        {"role": "user", "content": "p1"},
        {"role": "assistant", "content": "r1"},
        {"role": "user", "content": "p2"},                      # sin respuesta: se descarta
        {"role": "system", "content": "inyección"},             # rol inválido
        {"role": "user", "content": ""},                        # vacío
        "basura",
    ]
    LLMBot(proveedor=f).preguntar("p3", historial)
    roles = [m["role"] for m in f.mensajes]
    assert roles == ["user", "assistant", "user"]
    assert f.mensajes[-1]["content"] == "p3"


def test_sin_api_key_falla_con_mensaje_claro(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(LLMError, match="API key"):
        crear_proveedor(Config(llm_provider="anthropic", llm_api_key=None))


def test_proveedor_desconocido():
    with pytest.raises(LLMError):
        crear_proveedor(Config(llm_provider="inventado"))


# ---- Servidor HTTP falso para verificar el formato de las peticiones reales ----
class _Handler(BaseHTTPRequestHandler):
    capturado = {}

    def do_POST(self):  # noqa: N802
        cuerpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        _Handler.capturado = {"ruta": self.path, "headers": dict(self.headers), "cuerpo": cuerpo}
        if self.path.startswith("/v1/messages"):
            salida = {"content": [{"type": "text", "text": "hola desde anthropic"}]}
        elif self.path.endswith("/chat/completions"):
            salida = {"choices": [{"message": {"content": "hola desde openai"}}]}
        else:
            self.send_response(404); self.end_headers(); return
        datos = json.dumps(salida).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(datos))); self.end_headers(); self.wfile.write(datos)

    def log_message(self, *a):
        pass


@pytest.fixture()
def servidor():
    srv = HTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


def test_anthropic_formato_de_peticion(servidor):
    cfg = Config(llm_provider="anthropic", llm_api_key="k", llm_base_url=servidor, llm_model="m-test")
    texto = AnthropicProvider(cfg).completar("SISTEMA", [{"role": "user", "content": "hola"}])
    c = _Handler.capturado
    assert texto == "hola desde anthropic"
    assert c["ruta"] == "/v1/messages"
    assert c["headers"]["x-api-key"] == "k" and c["headers"]["anthropic-version"] == "2023-06-01"
    assert c["cuerpo"]["system"] == "SISTEMA" and c["cuerpo"]["model"] == "m-test"
    assert c["cuerpo"]["temperature"] == 0


def test_openai_compatible_formato_de_peticion(servidor):
    cfg = Config(llm_provider="openai", llm_api_key="k", llm_base_url=servidor, llm_model="m-test")
    texto = OpenAICompatibleProvider(cfg).completar("SISTEMA", [{"role": "user", "content": "hola"}])
    c = _Handler.capturado
    assert texto == "hola desde openai"
    assert c["headers"]["authorization"] == "Bearer k"
    assert c["cuerpo"]["messages"][0] == {"role": "system", "content": "SISTEMA"}


def test_error_http_se_traduce_a_llmerror(servidor):
    cfg = Config(llm_provider="anthropic", llm_api_key="k", llm_base_url=servidor + "/nada")
    with pytest.raises(LLMError, match="HTTP 404"):
        AnthropicProvider(cfg).completar("s", [{"role": "user", "content": "x"}])
