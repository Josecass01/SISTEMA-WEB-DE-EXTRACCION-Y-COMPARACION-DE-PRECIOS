"""Entidad de negocio EtiquetaDeAnaquel (Figura 13)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cadena_de_supermercados import CadenaDeSupermercados
    from .producto import Producto


class EtiquetaDeAnaquel:
    """Precio publicado por una cadena para un producto en una fecha."""

    def __init__(self, producto: Producto, cadena: CadenaDeSupermercados, precio: float,
                 precioPromocional: float | None, fecha: date,
                 pum: float | None = None, id: int | None = None):
        self.id = id
        self._producto = producto
        self._cadena = cadena
        self._precio = precio
        self._precioPromocional = precioPromocional
        self._fecha = fecha
        # El PUM se calcula una sola vez, durante la recolección, y se almacena
        # (Tabla 16). Al leer desde la base de datos se recibe el valor guardado.
        self._pum = pum if pum is not None else self.calcularPUM()

    @property
    def producto(self) -> Producto:
        return self._producto

    @property
    def cadena(self) -> CadenaDeSupermercados:
        return self._cadena

    @property
    def precio(self) -> float:
        return self._precio

    @property
    def precioPromocional(self) -> float | None:
        return self._precioPromocional

    @property
    def fecha(self) -> date:
        return self._fecha

    @property
    def pum(self) -> float:
        return self._pum

    def calcularPUM(self) -> float:
        """PUM = precio de lista / cantidad en unidad base (Circular Externa 011 de 2020)."""
        cantidad = self._producto.obtenerCantidadEnUnidadBase()
        if cantidad <= 0:
            raise ValueError("El contenido neto del producto debe ser mayor que cero.")
        return self._precio / cantidad
