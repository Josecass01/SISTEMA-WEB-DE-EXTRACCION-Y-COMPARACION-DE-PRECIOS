"""Controlador del caso de uso CU-S01 Comparar precios de un producto (Figuras 14 y 17)."""

from __future__ import annotations

import re

from src import configuracion
from src.negocio.componentes import ComparacionDePrecios, IComparacion
from src.presentacion.paginas import PaginaComparacion

CADENAS = ["Ara", "D1", "Olímpica"]


class CtrlComparacion:
    def __init__(self, comparacion: IComparacion | None = None, pagina: PaginaComparacion | None = None):
        self._comparacion = comparacion or ComparacionDePrecios()
        self._pagina = pagina or PaginaComparacion()

    def mostrar(self) -> str:
        return self._pagina.mostrar(cadenas=CADENAS, cadena=None, termino="")

    def buscar(self, termino: str, cadena: str | None) -> str:
        cadena = cadena if cadena in CADENAS else None
        datos = {"cadenas": CADENAS, "cadena": cadena, "termino": termino}
        if not self._validar(termino):
            return self._pagina.mostrar(mensaje="Ingrese el nombre de un producto.", error=True, **datos)

        etiquetas = self._comparacion.compararPrecios(termino, cadena)
        fecha = max((e.fecha for e in etiquetas), default=None)
        if not etiquetas:
            return self._pagina.mostrar(
                mensaje=f"No se encontraron productos para «{termino}». Revise el nombre e intente de nuevo.",
                **datos)
        orden = "ordenados del menor al mayor precio por unidad de medida (PUM)"
        if len(etiquetas) > configuracion.MAXIMO_RESULTADOS_BUSQUEDA:
            primeras = etiquetas[:configuracion.MAXIMO_RESULTADOS_BUSQUEDA]
            mensaje = (f"Se encontraron {len(etiquetas)} resultados para «{termino}». Se presentan los "
                       f"primeros {len(primeras)}, {orden}. Si desea ver otros, sea más específico.")
            return self._pagina.mostrar(resultados=primeras, mensaje=mensaje, fechaRecoleccion=fecha, **datos)
        mensaje = (f"Búsqueda completada. {len(etiquetas)} "
                   f"{'resultado encontrado' if len(etiquetas) == 1 else 'resultados encontrados'} "
                   f"para «{termino}», {orden}.")
        return self._pagina.mostrar(resultados=etiquetas, mensaje=mensaje, fechaRecoleccion=fecha, **datos)

    @staticmethod
    def _validar(termino: str) -> bool:
        """El término debe contener letras (Figura 17)."""
        return bool(re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", termino or ""))
