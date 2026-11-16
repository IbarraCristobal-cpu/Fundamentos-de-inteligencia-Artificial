"""Evalúa los dos chatbots con el set de 20 preguntas y guarda los resultados.

Uso (desde la raíz del repositorio):
    python -m evaluacion.evaluar                 # Prolog + LLM
    python -m evaluacion.evaluar --bots prolog   # solo Prolog
    python -m evaluacion.evaluar --bots llm      # solo LLM (conserva lo ya guardado de Prolog)

Genera:
    evaluacion/resultados.json   datos completos (insumo del informe)
    evaluacion/resultados.md     tabla legible con las 20 preguntas y respuestas

PUNTAJE AUTOMÁTICO: es una heurística (palabras clave y veredicto sí/no). Sirve como
primera revisión; las decisiones finales se registran en `revision_manual.json`
(ver README) y SIEMPRE deben leerse las respuestas completas antes de concluir.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
from datetime import datetime
from pathlib import Path

from backend.config import cargar_config
from backend.llm_bot import LLMBot
from backend.prolog_bot import PrologBot

AQUI = Path(__file__).resolve().parent
PREGUNTAS = AQUI / "preguntas.json"
RESULTADOS = AQUI / "resultados.json"
REVISION = AQUI / "revision_manual.json"
INFORME_MD = AQUI / "resultados.md"

MARCAS_RECHAZO = (
    "no entendi", "no esta en", "no tengo", "no cuento", "no puedo", "solo puedo", "no figura",
    "no esta modelad", "no se encuentra", "no contiene", "no dispongo", "base de conocimiento",
    "fuera de", "no esta incluid", "no incluye", "no hay informacion", "no tengo informacion",
)
NEGATIVO = re.compile(
    r"\bno (comete|incurre|infringe|esta infring|es (una )?infraccion|hay infraccion|constituye|"
    r"se considera|seria infraccion|puede ser multad|le pueden multar|me pueden multar)|"
    r"sin infraccion|dentro del limite|no excede|no supera|no sobrepasa"
)
POSITIVO = re.compile(r"infraccion|infringe|multa|excede|sobrepasa|supera")


def normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def puntuar(pregunta: dict, respuesta: str) -> tuple[str, str]:
    """Devuelve (veredicto, motivo) con veredicto en {"correcta", "incorrecta"}."""
    t = normalizar(respuesta)
    if pregunta["tipo"] == "rechazar":
        if any(m in t for m in MARCAS_RECHAZO):
            return "correcta", "reconoce que la consulta no está en su conocimiento"
        return "incorrecta", "responde en vez de reconocer que no tiene ese conocimiento"

    faltan = [c for c in pregunta.get("claves", []) if not any(alt in t for alt in c.split("|"))]
    if faltan:
        return "incorrecta", f"falta(n) dato(s) esperado(s): {', '.join(faltan)}"
    v = pregunta.get("veredicto")
    if v:
        negativo = bool(NEGATIVO.search(t))
        positivo = bool(POSITIVO.search(t)) and not negativo
        if v == "infraccion" and not positivo:
            return "incorrecta", "debía concluir que SÍ hay infracción"
        if v == "sin_infraccion" and not negativo:
            return "incorrecta", "debía concluir que NO hay infracción"
    return "correcta", "contiene los datos esperados"


def _cargar_json(ruta: Path, defecto):
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else defecto


def evaluar(bots: list[str], pausa: float) -> dict:
    preguntas = _cargar_json(PREGUNTAS, [])
    previo = _cargar_json(RESULTADOS, {})
    filas = {f["id"]: f for f in previo.get("preguntas", [])}
    config = cargar_config()
    meta = previo.get("meta", {})
    ejecutores = {}
    if "prolog" in bots:
        ejecutores["prolog"] = PrologBot(config).preguntar
    if "llm" in bots:
        llm = LLMBot(config)
        ejecutores["llm"] = lambda q: llm.preguntar(q)  # sin historial: preguntas independientes
        try:
            meta["llm"] = {"proveedor": config.llm_provider, "modelo": llm.proveedor.modelo,
                           "temperatura": config.llm_temperature}
        except Exception as exc:  # noqa: BLE001
            raise SystemExit(f"No se puede usar el LLM: {exc}") from exc

    for p in preguntas:
        fila = filas.setdefault(p["id"], {k: p[k] for k in ("id", "categoria", "pregunta", "esperada", "tipo")})
        for nombre, ejecutar in ejecutores.items():
            try:
                r = ejecutar(p["pregunta"])
                texto, error, ms = r.texto, None, r.ms
            except Exception as exc:  # noqa: BLE001
                texto, error, ms = "", str(exc), 0
            if error:
                fila[nombre] = {"respuesta": "", "error": error, "ms": 0, "auto": "error", "motivo": error}
            else:
                auto, motivo = puntuar(p, texto)
                fila[nombre] = {"respuesta": texto, "ms": ms, "auto": auto, "motivo": motivo}
            print(f"[{nombre:6}] P{p['id']:02d} {fila[nombre]['auto']:<10} {texto[:70]!r}")
            if nombre == "llm":
                time.sleep(pausa)

    meta["fecha"] = datetime.now().isoformat(timespec="seconds")
    resultado = {"meta": meta, "preguntas": [filas[i] for i in sorted(filas)]}
    aplicar_revision_manual(resultado)
    return resultado


def aplicar_revision_manual(resultado: dict) -> None:
    """`revision_manual.json`: {"prolog": {"18": "parcial"}, "llm": {...}} con notas opcionales."""
    rev = _cargar_json(REVISION, {})
    for fila in resultado["preguntas"]:
        for bot in ("prolog", "llm"):
            if bot not in fila:
                continue
            ajuste = rev.get(bot, {}).get(str(fila["id"]))
            if isinstance(ajuste, str):
                ajuste = {"final": ajuste}
            fila[bot]["final"] = (ajuste or {}).get("final", fila[bot]["auto"])
            if ajuste and ajuste.get("nota"):
                fila[bot]["nota"] = ajuste["nota"]


def resumen(resultado: dict) -> dict:
    out = {}
    for bot in ("prolog", "llm"):
        filas = [f[bot] for f in resultado["preguntas"] if bot in f]
        if not filas:
            continue
        cuenta = lambda v: sum(1 for f in filas if f.get("final", f["auto"]) == v)  # noqa: E731
        ms = [f["ms"] for f in filas if f["ms"]]
        out[bot] = {"correctas": cuenta("correcta"), "parciales": cuenta("parcial"),
                    "incorrectas": cuenta("incorrecta"), "errores": cuenta("error"),
                    "total": len(filas), "ms_promedio": round(sum(ms) / len(ms)) if ms else 0}
    return out


def a_markdown(resultado: dict) -> str:
    sim = {"correcta": "✅", "parcial": "🟡", "incorrecta": "❌", "error": "⚠️"}
    L = ["# Resultados de la evaluación (20 preguntas)", ""]
    m = resultado.get("meta", {})
    L.append(f"Fecha: {m.get('fecha', '?')}  ")
    if "llm" in m:
        L.append(f"LLM: {m['llm']['proveedor']} / {m['llm']['modelo']} (temperatura {m['llm']['temperatura']})  ")
    L += ["", "| Bot | Correctas | Parciales | Incorrectas | Errores | Tiempo medio |", "|---|---|---|---|---|---|"]
    for bot, r in resumen(resultado).items():
        L.append(f"| {bot} | {r['correctas']}/{r['total']} | {r['parciales']} | {r['incorrectas']} | {r['errores']} | {r['ms_promedio']} ms |")
    L.append("")
    for f in resultado["preguntas"]:
        L += [f"## P{f['id']}. {f['pregunta']}", f"*Categoría:* {f['categoria']}  ", f"*Respuesta esperada:* {f['esperada']}", ""]
        for bot in ("prolog", "llm"):
            if bot in f:
                b = f[bot]
                estado = b.get("final", b["auto"])
                L.append(f"- **{bot}** {sim.get(estado, '')} ({estado}, {b['ms']} ms): {b['respuesta'] or b.get('error', '')}".replace("\n", " "))
                if b.get("nota"):
                    L.append(f"  - Nota: {b['nota']}")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bots", nargs="+", choices=["prolog", "llm"], default=["prolog", "llm"])
    ap.add_argument("--pausa", type=float, default=0.5, help="segundos entre llamadas al LLM")
    args = ap.parse_args()
    res = evaluar(args.bots, args.pausa)
    RESULTADOS.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    INFORME_MD.write_text(a_markdown(res), encoding="utf-8")
    print("\nResumen:", json.dumps(resumen(res), ensure_ascii=False))
    print(f"Guardado en {RESULTADOS.name} y {INFORME_MD.name}")


if __name__ == "__main__":
    main()
