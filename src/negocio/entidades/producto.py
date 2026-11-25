"""Entidad de negocio Producto (Figura 13)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cadena_de_supermercados import CadenaDeSupermercados
    from .etiqueta_de_anaquel import EtiquetaDeAnaquel

# Factores para convertir el contenido neto a la unidad base (gramos o mililitros).
_FACTORES_UNIDAD_BASE = {
    "g": 1, "kg": 1000,
    "ml": 1, "l": 1000,
    "u": 1,
}


class Producto:
    """Artículo de consumo con su contenido neto y sus precios por cadena."""

    def __init__(self, descripcion: str, categoria: str, contenidoNeto: float,
                 unidadDeMedida: str, id: int | None = None):
        self.id = id  # identificador de objeto (OID) asignado por la base de datos
        self._descripcion = descripcion
        self._categoria = categoria
        self._contenidoNeto = contenidoNeto
        self._unidadDeMedida = unidadDeMedida.lower()
        # Asociación «Corresponde a» con EtiquetaDeAnaquel (navegable en ambos sentidos).
        self._etiquetas: list[EtiquetaDeAnaquel] = []

    # --- datos -------------------------------------------------------------
    @property
    def descripcion(self) -> str:
        return self._descripcion

    @property
    def categoria(self) -> str:
        return self._categoria

    @property
    def contenidoNeto(self) -> float:
        return self._contenidoNeto

    @property
    def unidadDeMedida(self) -> str:
        return self._unidadDeMedida

    def agregarEtiqueta(self, etiqueta: EtiquetaDeAnaquel) -> None:
        """Vincula una etiqueta de anaquel con el producto."""
        self._etiquetas.append(etiqueta)

    # --- operaciones de la Figura 13 ----------------------------------------
    def obtenerCantidadEnUnidadBase(self) -> float:
        """Contenido neto expresado en gramos, mililitros o unidades."""
        return self._contenidoNeto * _FACTORES_UNIDAD_BASE.get(self._unidadDeMedida, 1)

    def obtenerPrecioVigente(self, cadena: CadenaDeSupermercados) -> EtiquetaDeAnaquel | None:
        """Etiqueta más reciente del producto en la cadena, o None si no la tiene."""
        etiquetas = [e for e in self._etiquetas if e.cadena.nombre == cadena.nombre]
        return max(etiquetas, key=lambda e: e.fecha) if etiquetas else None

    def obtenerPreciosOrdenadosPorPUM(self) -> list[EtiquetaDeAnaquel]:
        """Precio vigente de cada cadena, ordenado de menor a mayor PUM."""
        vigentes: dict[str, EtiquetaDeAnaquel] = {}
        for etiqueta in self._etiquetas:
            actual = vigentes.get(etiqueta.cadena.nombre)
            if actual is None or etiqueta.fecha > actual.fecha:
                vigentes[etiqueta.cadena.nombre] = etiqueta
        return sorted(vigentes.values(), key=lambda e: e.pum)

    def obtenerHistorial(self, fechaInicio: date, fechaFin: date) -> list[EtiquetaDeAnaquel]:
        """Etiquetas del producto en el intervalo, ordenadas por fecha."""
        return sorted(
            (e for e in self._etiquetas if fechaInicio <= e.fecha <= fechaFin),
            key=lambda e: (e.fecha, e.cadena.nombre),
        )
