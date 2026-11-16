import pytest

from evaluacion.evaluar import normalizar, puntuar

INFR = {"tipo": "responder", "veredicto": "infraccion", "claves": ["20"]}
SIN = {"tipo": "responder", "veredicto": "sin_infraccion", "claves": []}
RECH = {"tipo": "rechazar"}


@pytest.mark.parametrize("texto,pregunta,esperado", [
    ("Sí, comete infracción: excede el límite de 50 km/h en 20 km/h (Regla 2).", INFR, "correcta"),
    ("No comete infracción, va dentro del límite.", INFR, "incorrecta"),
    ("No, no comete infracción porque 50 no es mayor que 50.", SIN, "correcta"),
    ("Sí, comete infracción al exceder el límite.", SIN, "incorrecta"),
    ("Eso no está en mi base de conocimiento.", RECH, "correcta"),
    ("La multa es de 1 a 1,5 UTM.", RECH, "incorrecta"),
])
def test_puntuacion(texto, pregunta, esperado):
    assert puntuar(pregunta, texto)[0] == esperado


def test_normalizar_quita_tildes():
    assert normalizar("Camión ÚRBANA") == "camion urbana"


def test_claves_alternativas():
    p = {"tipo": "responder", "claves": ["urbana|ciudad"]}
    assert puntuar(p, "Solo en la ciudad")[0] == "correcta"
    assert puntuar(p, "En ninguno")[0] == "incorrecta"
