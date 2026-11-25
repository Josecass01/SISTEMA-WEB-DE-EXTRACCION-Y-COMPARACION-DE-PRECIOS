"""Componente de acceso a datos de las cadenas y sus tiendas (Figura 15)."""

from __future__ import annotations

from pathlib import Path

from src.negocio.entidades import CadenaDeSupermercados, Tienda

from .conexion import abrir
from .interfaces import ICadenaDAC


class CadenaDAC(ICadenaDAC):
    def __init__(self, ruta: Path | None = None):
        self._ruta = ruta

    def obtenerCadenas(self) -> list[CadenaDeSupermercados]:
        with abrir(self._ruta) as conexion:
            filas = conexion.execute(
                "SELECT id_cadena, nombre FROM cadena_supermercado ORDER BY nombre").fetchall()
        return [CadenaDeSupermercados(f["nombre"], id=f["id_cadena"]) for f in filas]

    def obtenerTiendas(self) -> list[Tienda]:
        cadenas = {c.id: c for c in self.obtenerCadenas()}
        with abrir(self._ruta) as conexion:
            filas = conexion.execute(
                "SELECT id_tienda, id_cadena, nombre, direccion, latitud, longitud FROM tienda").fetchall()
        return [Tienda(f["nombre"], f["direccion"], f["latitud"], f["longitud"],
                       cadena=cadenas.get(f["id_cadena"]), id=f["id_tienda"]) for f in filas]
