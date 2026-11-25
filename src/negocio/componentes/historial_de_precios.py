"""Componente de negocio HistorialDePrecios (Figura 14, CU-S03)."""

from __future__ import annotations

from datetime import date

from src.datos.acceso import IProductoDAC, ProductoDAC
from src.negocio.entidades import EtiquetaDeAnaquel

from .interfaces import IHistorial


class HistorialDePrecios(IHistorial):
    def __init__(self, productoDAC: IProductoDAC | None = None):
        self._productoDAC = productoDAC or ProductoDAC()

    def consultar(self, idProducto: int, fechaInicio: date, fechaFin: date) -> list[EtiquetaDeAnaquel]:
        producto = self._productoDAC.obtenerConHistorial(idProducto, fechaInicio, fechaFin)
        if producto is None:
            return []
        # El historial se obtiene de la entidad Producto (Figura 19).
        return producto.obtenerHistorial(fechaInicio, fechaFin)
