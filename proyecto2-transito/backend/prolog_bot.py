"""Chatbot #1: lógica de primer orden (SWI-Prolog) invocado como subproceso.

Cada pregunta lanza `swipl prolog/una_pregunta.pl`, de modo que cualquier cambio
en los archivos .pl se refleja de inmediato, sin reiniciar el servidor.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import time
from dataclasses import dataclass

from .config import Config, cargar_config


class PrologNoDisponible(RuntimeError):
    """No se encontró SWI-Prolog o el subproceso falló."""


@dataclass
class RespuestaBot:
    texto: str
    ms: int
    meta: dict


def _buscar_swipl(config: Config) -> str:
    candidatos = [config.swipl_path, shutil.which("swipl")]
    if os.name == "nt":  # rutas típicas de instalación en Windows
        candidatos += [
            r"C:\Program Files\swipl\bin\swipl.exe",
            r"C:\Program Files (x86)\swipl\bin\swipl.exe",
        ]
    for ruta in candidatos:
        if ruta and (shutil.which(ruta) or os.path.isfile(ruta)):
            return ruta
    raise PrologNoDisponible(
        "No se encontró SWI-Prolog. Instálalo o define SWIPL_PATH en el archivo .env."
    )


class PrologBot:
    nombre = "prolog"

    def __init__(self, config: Config | None = None):
        self.config = config or cargar_config()

    def preguntar(self, texto: str) -> RespuestaBot:
        swipl = _buscar_swipl(self.config)
        inicio = time.perf_counter()
        try:
            proc = subprocess.run(
                [swipl, str(self.config.prolog_script)],
                input=texto.replace("\n", " ").strip().encode("utf-8"),
                capture_output=True,
                timeout=self.config.prolog_timeout,
                cwd=self.config.prolog_script.parent,
            )
        except subprocess.TimeoutExpired as exc:
            raise PrologNoDisponible("SWI-Prolog tardó demasiado en responder.") from exc
        ms = int((time.perf_counter() - inicio) * 1000)

        salida = proc.stdout.decode("utf-8", errors="replace")
        if proc.returncode != 0 or not salida.strip():
            detalle = proc.stderr.decode("utf-8", errors="replace").strip()[:300]
            raise PrologNoDisponible(f"Error al ejecutar Prolog: {detalle or 'sin salida'}")

        intencion, _, respuesta = salida.partition("\n")
        return RespuestaBot(texto=respuesta.strip(), ms=ms, meta={"intencion": intencion.strip()})
