import shutil

import pytest

from backend.prolog_bot import PrologBot

pytestmark = pytest.mark.skipif(shutil.which("swipl") is None, reason="SWI-Prolog no instalado")

CASOS = [
    ("¿Cuál es el límite de velocidad en zona urbana?", "50 km/h"),
    ("¿Qué velocidad máxima hay en zona escolar?", "30 km/h"),
    ("¿A qué velocidad máxima puede ir un camión en zona rural?", "90 km/h"),
    ("¿Comete infracción un auto a 70 km/h en zona urbana?", "Comete infracción"),
    ("¿Comete infracción un auto a 50 km/h en zona urbana?", "No comete infracción"),
    ("¿Qué debe hacer un auto frente a un disco pare?", "detenerse"),
    ("¿Qué debe hacer un camión ante un ceda el paso?", "ceder"),
    ("¿Qué señales obligan a detenerse?", "Disco Pare, Luz Roja"),
    ("Un auto y un camión llegan al mismo tiempo a un cruce sin señalizar, el camión viene por la derecha. ¿Quién pasa primero?", "Tiene preferencia un camión"),
]


@pytest.mark.parametrize("pregunta,esperado", CASOS)
def test_respuestas_correctas(pregunta, esperado):
    assert esperado in PrologBot().preguntar(pregunta).texto


def test_fuera_de_alcance():
    r = PrologBot().preguntar("¿Cuál es la capital de Francia?")
    assert "No entendí" in r.texto
    assert r.meta["intencion"] == "desconocida"


def test_entrada_vacia_o_rara_no_rompe():
    bot = PrologBot()
    for texto in ["", "   ", "¿¿¿???", "'; halt. %", "a" * 400, "🚗🚗🚗"]:
        assert bot.preguntar(texto).texto  # siempre responde algo


def test_cada_pregunta_es_independiente():
    bot = PrologBot()
    bot.preguntar("¿Comete infracción un camión a 95 km/h en zona rural?")
    # si el escenario anterior quedara cargado, esto cambiaría
    assert "No comete infracción" in bot.preguntar("¿Comete infracción un camión a 80 km/h en zona rural?").texto
