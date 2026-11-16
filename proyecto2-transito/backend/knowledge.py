"""Carga del conocimiento en lenguaje natural que se entrega al LLM.

El archivo se vuelve a leer cuando cambia en disco, así que editar
`conocimiento/transito.md` surte efecto sin reiniciar el servidor.
"""
from __future__ import annotations

from pathlib import Path


class Conocimiento:
    def __init__(self, ruta: Path):
        self.ruta = Path(ruta)
        self._mtime: float | None = None
        self._texto = ""

    def texto(self) -> str:
        mtime = self.ruta.stat().st_mtime
        if mtime != self._mtime:
            self._texto = self.ruta.read_text(encoding="utf-8")
            self._mtime = mtime
        return self._texto
