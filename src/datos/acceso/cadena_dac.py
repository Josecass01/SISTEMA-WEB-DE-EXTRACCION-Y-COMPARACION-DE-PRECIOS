"""CadenaDAC, EtiquetaDAC y RecoleccionDAC."""

from __future__ import annotations

from src.negocio.entidades import (CadenaDeSupermercados, EtiquetaDeAnaquel, ResultadoDeRecoleccion,
                                   Tienda)

from .conexion import conectar
from .interfaces import ICadenaDAC, IEtiquetaDAC, IRecoleccionDAC


class CadenaDAC(ICadenaDAC):
    def obtenerCadenas(self) -> list[CadenaDeSupermercados]:
        with conectar() as conexion:
            filas = conexion.execute("SELECT id_cadena, nombre FROM cadena_supermercado ORDER BY nombre").fetchall()
        return [CadenaDeSupermercados(f["nombre"], id=f["id_cadena"]) for f in filas]

    def obtenerTiendas(self) -> list[Tienda]:
        cadenas = {c.id: c for c in self.obtenerCadenas()}
        with conectar() as conexion:
            filas = conexion.execute("SELECT * FROM tienda ORDER BY id_tienda").fetchall()
        return [Tienda(f["nombre"], f["direccion"], f["latitud"], f["longitud"],
                       cadena=cadenas.get(f["id_cadena"]), id=f["id_tienda"]) for f in filas]


class EtiquetaDAC(IEtiquetaDAC):
    def guardar(self, etiquetas: list[EtiquetaDeAnaquel]) -> None:
        """Guarda las etiquetas en una sola transacción; reemplaza la del mismo día."""
        if not etiquetas:
            return
        with conectar() as conexion:
            conexion.executemany(
                """INSERT OR REPLACE INTO etiqueta_anaquel
                   (id_producto, id_cadena, fecha, precio, precio_promocional, pum)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [(e.producto.id, e.cadena.id, e.fecha.isoformat(), e.precio, e.precioPromocional, e.pum)
                 for e in etiquetas])


class RecoleccionDAC(IRecoleccionDAC):
    def guardarResultado(self, resultado: ResultadoDeRecoleccion) -> None:
        with conectar() as conexion:
            conexion.execute(
                """INSERT INTO resultado_recoleccion (id_cadena, fecha, estado, registros_procesados)
                   VALUES (?, ?, ?, ?)""",
                (resultado.cadena.id, resultado.fecha.isoformat(), resultado.estado,
                 resultado.registrosProcesados))
