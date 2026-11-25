"""Entidad de negocio ResultadoDeRecoleccion (Figura 13)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cadena_de_supermercados import CadenaDeSupermercados


class ResultadoDeRecoleccion:
    """Registro (bitácora) del resultado de la recolección de una cadena en una fecha."""

    FINALIZADA = "finalizada"
    PAUSADA = "pausada"

    def __init__(self, cadena: CadenaDeSupermercados, fecha: date, estado: str,
                 registrosProcesados: int = 0, id: int | None = None):
        self.id = id
        self._cadena = cadena
        self._fecha = fecha
        self._estado = estado
        self._registrosProcesados = registrosProcesados

    @property
    def cadena(self) -> CadenaDeSupermercados:
        return self._cadena

    @property
    def fecha(self) -> date:
        return self._fecha

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def registrosProcesados(self) -> int:
        return self._registrosProcesados
