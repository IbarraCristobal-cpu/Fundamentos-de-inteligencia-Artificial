import pytest

from backend.app import crear_app
from backend.llm_providers import LLMError
from backend.prolog_bot import RespuestaBot


class BotOk:
    def __init__(self, texto="ok", meta=None):
        self.texto, self.meta = texto, meta or {}

    def preguntar(self, pregunta, historial=None):
        return RespuestaBot(texto=self.texto, ms=1, meta=self.meta)


class BotRoto:
    def __init__(self, exc):
        self.exc = exc

    def preguntar(self, *a, **k):
        raise self.exc


def cliente(prolog=None, llm=None):
    app = crear_app(prolog_bot=prolog or BotOk("p", {"intencion": "x"}), llm_bot=llm or BotOk("l", {"modelo": "m"}))
    return app.test_client()


def test_modo_ambos():
    r = cliente().post("/api/chat", json={"pregunta": "hola", "modo": "ambos"})
    j = r.get_json()
    assert r.status_code == 200 and j["prolog"]["respuesta"] == "p" and j["llm"]["respuesta"] == "l"


@pytest.mark.parametrize("modo,ausente", [("prolog", "llm"), ("llm", "prolog")])
def test_modo_unico(modo, ausente):
    j = cliente().post("/api/chat", json={"pregunta": "hola", "modo": modo}).get_json()
    assert modo in j and ausente not in j


@pytest.mark.parametrize("cuerpo", [{}, {"pregunta": ""}, {"pregunta": "   "}, {"pregunta": "a" * 501},
                                    {"pregunta": "hola", "modo": "otro"}])
def test_entradas_invalidas(cuerpo):
    assert cliente().post("/api/chat", json=cuerpo).status_code == 400


def test_json_invalido():
    assert cliente().post("/api/chat", data="no es json", content_type="application/json").status_code == 400


def test_un_bot_caido_no_tumba_al_otro():
    c = cliente(llm=BotRoto(LLMError("sin credenciales")))
    j = c.post("/api/chat", json={"pregunta": "hola", "modo": "ambos"}).get_json()
    assert j["prolog"]["ok"] is True
    assert j["llm"] == {"ok": False, "error": "sin credenciales"}


def test_error_inesperado_no_filtra_detalles():
    c = cliente(prolog=BotRoto(ValueError("secreto interno")))
    j = c.post("/api/chat", json={"pregunta": "hola", "modo": "prolog"}).get_json()
    assert j["prolog"]["ok"] is False and "secreto" not in j["prolog"]["error"]


def test_frontend_se_sirve():
    r = cliente().get("/")
    assert r.status_code == 200 and b"TransitoBot" in r.data
