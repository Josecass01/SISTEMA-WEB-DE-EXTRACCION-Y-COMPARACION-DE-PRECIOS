"""Entidades de negocio ListaDeCompras e ItemDeLista (Figura 13)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cadena_de_supermercados import CadenaDeSupermercados
    from .producto import Producto


def _esMismoProducto(a: Producto, b: Producto) -> bool:
    """Dos objetos representan el mismo producto si comparten su identificador (OID)."""
    return a is b or (a.id is not None and a.id == b.id)


class ItemDeLista:
    """Producto de la lista con la cantidad solicitada."""

    def __init__(self, producto: Producto, cantidad: int):
        self._producto = producto
        self._cantidad = cantidad

    @property
    def producto(self) -> Producto:
        return self._producto

    @property
    def cantidad(self) -> int:
        return self._cantidad

    def calcularSubtotal(self, cadena: CadenaDeSupermercados) -> float | None:
        """Precio vigente × cantidad; None si la cadena no tiene el producto."""
        etiqueta = self._producto.obtenerPrecioVigente(cadena)
        if etiqueta is None:
            return None
        return etiqueta.precio * self._cantidad


class ListaDeCompras:
    """Conjunto de productos que el comprador desea evaluar. No se almacena."""

    def __init__(self):
        # Composición «Contiene» con ItemDeLista.
        self._items: list[ItemDeLista] = []

    @property
    def items(self) -> list[ItemDeLista]:
        return list(self._items)

    def agregarItem(self, producto: Producto, cantidad: int) -> ItemDeLista:
        """Crea el ítem de la lista (patrón Creador); si ya existe, suma la cantidad."""
        for posicion, item in enumerate(self._items):
            if _esMismoProducto(item.producto, producto):
                self._items[posicion] = ItemDeLista(producto, item.cantidad + cantidad)
                return self._items[posicion]
        item = ItemDeLista(producto, cantidad)
        self._items.append(item)
        return item

    def quitarItem(self, producto: Producto) -> None:
        self._items = [i for i in self._items if not _esMismoProducto(i.producto, producto)]

    def calcularCostoTotal(self, cadena: CadenaDeSupermercados) -> tuple[float, list[ItemDeLista]]:
        """
        Costo total = Σ (precio del producto en la cadena × cantidad).

        Devuelve el total y los ítems que la cadena no tiene, que no se suman
        como cero sino que se informan (CU-S02, extensión 5a).
        """
        total = 0.0
        faltantes: list[ItemDeLista] = []
        for item in self._items:
            subtotal = item.calcularSubtotal(cadena)
            if subtotal is None:
                faltantes.append(item)
            else:
                total += subtotal
        return total, faltantes
