"""Componente de negocio EvaluacionDeLista (Figura 14, CU-S02)."""

from __future__ import annotations

from dataclasses import dataclass, field

from src import configuracion
from src.datos.acceso import CadenaDAC, ICadenaDAC, IProductoDAC, ProductoDAC
from src.negocio.entidades import (CadenaDeSupermercados, Comprador, ItemDeLista,
                                   ListaDeCompras, Producto)

from .interfaces import IListaDeCompras


class ListaLlena(Exception):
    """La lista alcanzó el máximo de productos definido en el diseño (Tabla 18)."""


@dataclass
class CostoPorCadena:
    """Resultado de la evaluación de la lista en una cadena."""

    cadena: CadenaDeSupermercados
    costoTotal: float
    noIncluidos: list[ItemDeLista] = field(default_factory=list)
    esLaMasEconomica: bool = False

    @property
    def incluyeTodos(self) -> bool:
        return not self.noIncluidos


class EvaluacionDeLista(IListaDeCompras):
    def __init__(self, productoDAC: IProductoDAC | None = None, cadenaDAC: ICadenaDAC | None = None):
        self._productoDAC = productoDAC or ProductoDAC()
        self._cadenaDAC = cadenaDAC or CadenaDAC()
        self.lista: ListaDeCompras | None = None

    def iniciarLista(self) -> None:
        # Comprador crea la lista (patrón Creador, Figura 18).
        self.lista = Comprador().crearListaDeCompras()

    def agregarProducto(self, nombre: str, cantidad: int) -> Producto | None:
        """Agrega el producto a la lista; None si no se encuentra registrado (CU-S02, 2b)."""
        if self.lista is None:
            self.iniciarLista()
        producto = self._productoDAC.buscarPorNombre(nombre)
        if producto is None:
            return None
        ya_esta = any(i.producto.id == producto.id for i in self.lista.items)
        if not ya_esta and len(self.lista.items) >= configuracion.MAXIMO_PRODUCTOS_POR_LISTA:
            raise ListaLlena()
        self.lista.agregarItem(producto, cantidad)
        return producto

    def quitarProducto(self, nombre: str) -> None:
        for item in self.lista.items if self.lista else []:
            if item.producto.descripcion == nombre:
                self.lista.quitarItem(item.producto)

    def evaluarLista(self) -> list[CostoPorCadena]:
        """Costo total de la lista en cada cadena, con la opción más económica destacada."""
        resultados = []
        for cadena in self._cadenaDAC.obtenerCadenas():
            total, faltantes = self.lista.calcularCostoTotal(cadena)
            resultados.append(CostoPorCadena(cadena, total, faltantes))
        self._determinarOpcionMasEconomica(resultados)
        # Primero las cadenas que tienen todos los productos, de la más económica a la más costosa.
        return sorted(resultados, key=lambda r: (not r.incluyeTodos, len(r.noIncluidos), r.costoTotal))

    @staticmethod
    def _determinarOpcionMasEconomica(resultados: list[CostoPorCadena]) -> None:
        """Una cadena a la que le falta un producto no se ubica como la más económica (RF, 3.2.4)."""
        completas = [r for r in resultados if r.incluyeTodos]
        if completas:
            min(completas, key=lambda r: r.costoTotal).esLaMasEconomica = True
