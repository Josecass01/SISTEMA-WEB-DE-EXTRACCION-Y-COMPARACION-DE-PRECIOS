"""Componente de acceso a datos de la bitácora de la recolección (Figura 15)."""

from __future__ import annotations

from pathlib import Path

from src.negocio.entidades import ResultadoDeRecoleccion

from .conexion import abrir
from .interfaces import IRecoleccionDAC


class RecoleccionDAC(IRecoleccionDAC):
    def __init__(self, ruta: Path | None = None):
        self._ruta = ruta

    def guardarResultado(self, resultado: ResultadoDeRecoleccion) -> None:
        with abrir(self._ruta) as conexion:
            conexion.execute(
                """INSERT INTO resultado_recoleccion (id_cadena, fecha, estado, registros_procesados)
                   VALUES (?, ?, ?, ?)""",
                (resultado.cadena.id, resultado.fecha.isoformat(), resultado.estado,
                 resultado.registrosProcesados),
            )
