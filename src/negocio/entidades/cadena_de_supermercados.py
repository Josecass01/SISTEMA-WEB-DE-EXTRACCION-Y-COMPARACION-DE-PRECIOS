"""Entidad de negocio CadenaDeSupermercados (Figura 13)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from .etiqueta_de_anaquel import EtiquetaDeAnaquel

if TYPE_CHECKING:
    from .producto import Producto


class CadenaDeSupermercados:
    """Empresa que opera tiendas bajo una misma marca y publica sus precios."""

    def __init__(self, nombre: str, id: int | None = None):
        self.id = id
        self._nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    def registrarPrecio(self, producto: Producto, precio: float, precioPromocional: float | None,
                        fecha: date) -> EtiquetaDeAnaquel:
        """Crea la etiqueta de anaquel del producto (patrón Creador)."""
        etiqueta = EtiquetaDeAnaquel(producto, self, precio, precioPromocional, fecha)
        producto.agregarEtiqueta(etiqueta)
        return etiqueta
