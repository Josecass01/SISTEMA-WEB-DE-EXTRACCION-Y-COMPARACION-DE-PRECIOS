"""Componente de negocio ComparacionDePrecios (Figura 14, CU-S01)."""

from __future__ import annotations

from src.datos.acceso import IProductoDAC, ProductoDAC
from src.negocio.entidades import EtiquetaDeAnaquel

from .interfaces import IComparacion


class ComparacionDePrecios(IComparacion):
    def __init__(self, productoDAC: IProductoDAC | None = None):
        self._productoDAC = productoDAC or ProductoDAC()

    def compararPrecios(self, termino: str, cadena: str | None) -> list[EtiquetaDeAnaquel]:
        """Opciones encontradas en los supermercados, de menor a mayor PUM."""
        etiquetas: list[EtiquetaDeAnaquel] = []
        for producto in self._productoDAC.buscar(termino, cadena):
            # El experto en los precios del producto es Producto (Figura 17).
            etiquetas.extend(producto.obtenerPreciosOrdenadosPorPUM())
        return self._ordenarPorPUM(etiquetas)

    @staticmethod
    def _ordenarPorPUM(etiquetas: list[EtiquetaDeAnaquel]) -> list[EtiquetaDeAnaquel]:
        return sorted(etiquetas, key=lambda e: (e.pum, e.precio))
