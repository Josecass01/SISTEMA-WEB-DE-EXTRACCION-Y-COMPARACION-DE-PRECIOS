"""Componente de acceso a datos de las etiquetas de anaquel (historial de precios, Figura 15)."""

from __future__ import annotations

from pathlib import Path

from src.negocio.entidades import EtiquetaDeAnaquel

from .conexion import abrir
from .interfaces import IEtiquetaDAC


class EtiquetaDAC(IEtiquetaDAC):
    def __init__(self, ruta: Path | None = None):
        self._ruta = ruta

    def guardar(self, etiquetas: list[EtiquetaDeAnaquel]) -> None:
        """
        Almacena las etiquetas de una cadena en una sola transacción (Tabla 16).
        Si ya existe el precio del día, se actualiza (CU-S05, extensión 3a).
        """
        with abrir(self._ruta) as conexion:  # confirma o deshace todo el bloque
            conexion.executemany(
                """INSERT INTO etiqueta_anaquel
                       (id_producto, id_cadena, fecha, precio, precio_promocional, pum)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT (id_producto, id_cadena, fecha) DO UPDATE SET
                       precio = excluded.precio,
                       precio_promocional = excluded.precio_promocional,
                       pum = excluded.pum""",
                [(e.producto.id, e.cadena.id, e.fecha.isoformat(), e.precio,
                  e.precioPromocional, e.pum) for e in etiquetas],
            )
