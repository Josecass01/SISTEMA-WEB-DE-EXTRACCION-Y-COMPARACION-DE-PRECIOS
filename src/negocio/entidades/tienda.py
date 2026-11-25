"""Entidad de negocio Tienda (Figura 13)."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cadena_de_supermercados import CadenaDeSupermercados

RADIO_TERRESTRE_KM = 6371.0


class Tienda:
    """Sucursal física de una cadena, con su posición geográfica."""

    def __init__(self, nombre: str, direccion: str, latitud: float, longitud: float,
                 cadena: CadenaDeSupermercados | None = None, id: int | None = None):
        self.id = id
        self._nombre = nombre
        self._direccion = direccion
        self._latitud = latitud
        self._longitud = longitud
        self._cadena = cadena

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def direccion(self) -> str:
        return self._direccion

    @property
    def cadena(self) -> CadenaDeSupermercados | None:
        return self._cadena

    def calcularDistancia(self, latitud: float, longitud: float) -> float:
        """Distancia en kilómetros con la fórmula del semiverseno (Tabla 18)."""
        lat1, lat2 = math.radians(latitud), math.radians(self._latitud)
        dlat = lat2 - lat1
        dlon = math.radians(self._longitud - longitud)
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return 2 * RADIO_TERRESTRE_KM * math.asin(math.sqrt(a))
