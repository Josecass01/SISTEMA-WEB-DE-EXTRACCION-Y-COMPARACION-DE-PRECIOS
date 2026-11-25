"""Controlador del caso de uso CU-S02 Evaluar lista de compras (Figuras 14 y 18)."""

from __future__ import annotations

from src import configuracion
from src.negocio.componentes import EvaluacionDeLista, IListaDeCompras, ListaLlena
from src.presentacion.paginas import PaginaListaDeCompras


class CtrlListaDeCompras:
    def __init__(self, evaluacion: IListaDeCompras | None = None, pagina: PaginaListaDeCompras | None = None):
        self._evaluacion = evaluacion or EvaluacionDeLista()
        self._pagina = pagina or PaginaListaDeCompras()

    def iniciarLista(self) -> str:
        self._evaluacion.iniciarLista()
        return self._mostrar()

    def mostrar(self) -> str:
        if self._evaluacion.lista is None:
            self._evaluacion.iniciarLista()
        return self._mostrar()

    def agregarProducto(self, nombre: str, cantidad: str | int) -> str:
        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            cantidad = 0
        if cantidad <= 0:  # CU-S02, extensión 2a
            return self._mostrar(mensaje="La cantidad debe ser mayor que cero.", error=True,
                                 nombre=nombre, cantidad=cantidad)
        if not (nombre or "").strip():
            return self._mostrar(mensaje="Ingrese el nombre del producto.", error=True, cantidad=cantidad)
        try:
            producto = self._evaluacion.agregarProducto(nombre, cantidad)
        except ListaLlena:
            return self._mostrar(
                mensaje=f"La lista admite un máximo de {configuracion.MAXIMO_PRODUCTOS_POR_LISTA} productos.",
                error=True)
        if producto is None:  # CU-S02, extensión 2b
            return self._mostrar(mensaje=f"Producto no encontrado: «{nombre}». No se agregó a la lista.",
                                 error=True, nombre=nombre, cantidad=cantidad)
        return self._mostrar(mensaje=f"Se agregó «{producto.descripcion}» a la lista.")

    def quitarProducto(self, nombre: str) -> str:
        self._evaluacion.quitarProducto(nombre)
        return self._mostrar(mensaje=f"Se quitó «{nombre}» de la lista.")

    def evaluarLista(self) -> str:
        if not self._evaluacion.lista or not self._evaluacion.lista.items:  # CU-S02, extensión 4a
            return self._mostrar(mensaje="La lista debe contener al menos un producto.", error=True)
        costos = self._evaluacion.evaluarLista()
        fechas = [e.fecha for i in self._evaluacion.lista.items
                  for e in i.producto.obtenerPreciosOrdenadosPorPUM()]
        return self._mostrar(costos=costos, fechaRecoleccion=max(fechas, default=None),
                             mensaje="Costo total de la lista en cada supermercado.")

    def _mostrar(self, **datos) -> str:
        items = self._evaluacion.lista.items if self._evaluacion.lista else []
        return self._pagina.mostrar(items=items, **datos)
