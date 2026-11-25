"""Componente de negocio UbicacionDeTiendas (Figura 14, CU-S04)."""

from __future__ import annotations

from src import configuracion
from src.datos.acceso import CadenaDAC, ICadenaDAC
from src.negocio.entidades import Tienda

from .interfaces import IUbicacion


class UbicacionDeTiendas(IUbicacion):
    def __init__(self, cadenaDAC: ICadenaDAC | None = None):
        self._cadenaDAC = cadenaDAC or CadenaDAC()
        self._tiendasConDistancia: list[tuple[Tienda, float]] = []

    def ubicar(self, latitud: float, longitud: float) -> list[tuple[Tienda, float]]:
        """
        Tiendas dentro del radio de cobertura (Tabla 18), de la más cercana a la
        más lejana. La posición solo se usa como parámetro y no se almacena.
        """
        self._tiendasConDistancia = []
        for tienda in self._cadenaDAC.obtenerTiendas():
            distancia = tienda.calcularDistancia(latitud, longitud)  # experto: Tienda
            if distancia <= configuracion.RADIO_DE_COBERTURA_KM:
                self._tiendasConDistancia.append((tienda, distancia))
        self._ordenarPorDistancia()
        return self._tiendasConDistancia

    def _ordenarPorDistancia(self) -> None:
        self._tiendasConDistancia.sort(key=lambda par: par[1])
