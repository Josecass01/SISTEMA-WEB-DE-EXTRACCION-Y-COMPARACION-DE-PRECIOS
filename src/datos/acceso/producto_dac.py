"""ProductoDAC: lectura y registro de productos con sus etiquetas de anaquel."""

from __future__ import annotations

import sqlite3
import unicodedata
from datetime import date
from typing import TYPE_CHECKING

from src.negocio.entidades import CadenaDeSupermercados, EtiquetaDeAnaquel, Producto

from .conexion import conectar
from .interfaces import IProductoDAC

if TYPE_CHECKING:
    from src.datos.agentes.agente_de_supermercado import ProductoPublicado


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes y con espacios simples, para comparar nombres."""
    sin_tildes = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return " ".join(sin_tildes.lower().split())


def _producto(fila: sqlite3.Row) -> Producto:
    return Producto(fila["descripcion"], fila["categoria"], fila["contenido_neto"],
                    fila["unidad_medida"], id=fila["id_producto"])


class ProductoDAC(IProductoDAC):
    # --- consultas --------------------------------------------------------
    def buscar(self, termino: str, cadena: str | None = None) -> list[Producto]:
        """Productos cuya descripción contiene todas las palabras del término."""
        palabras = normalizar(termino).split()
        if not palabras:
            return []
        with conectar() as conexion:
            filas = conexion.execute(
                "SELECT * FROM producto WHERE id_producto IN (SELECT DISTINCT id_producto FROM etiqueta_anaquel)"
            ).fetchall()
            productos = [_producto(f) for f in filas
                         if all(p in normalizar(f["descripcion"]) for p in palabras)]
            self._cargarEtiquetas(conexion, productos, cadena=cadena)
        return [p for p in productos if p.obtenerPreciosOrdenadosPorPUM()]

    def buscarPorNombre(self, nombre: str) -> Producto | None:
        """Producto con ese nombre (sin distinguir mayúsculas ni tildes) y sus precios."""
        buscado = normalizar(nombre)
        if not buscado:
            return None
        with conectar() as conexion:
            filas = conexion.execute(
                "SELECT * FROM producto WHERE id_producto IN (SELECT DISTINCT id_producto FROM etiqueta_anaquel)"
            ).fetchall()
            exactos = [f for f in filas if normalizar(f["descripcion"]) == buscado]
            if not exactos:
                palabras = buscado.split()
                exactos = sorted((f for f in filas if all(p in normalizar(f["descripcion"]) for p in palabras)),
                                 key=lambda f: len(f["descripcion"]))
            if not exactos:
                return None
            producto = _producto(exactos[0])
            self._cargarEtiquetas(conexion, [producto])
        return producto

    def obtenerConHistorial(self, idProducto: int, fechaInicio: date, fechaFin: date) -> Producto | None:
        with conectar() as conexion:
            fila = conexion.execute("SELECT * FROM producto WHERE id_producto = ?", (idProducto,)).fetchone()
            if fila is None:
                return None
            producto = _producto(fila)
            self._cargarEtiquetas(conexion, [producto], fechaInicio=fechaInicio, fechaFin=fechaFin)
        return producto

    # --- registro (recolección) -------------------------------------------
    def obtenerOCrear(self, datos: ProductoPublicado) -> Producto:
        """Producto registrado con la misma descripción y contenido; si no existe, se crea."""
        with conectar() as conexion:
            fila = conexion.execute(
                """SELECT * FROM producto
                   WHERE lower(descripcion) = lower(?) AND unidad_medida = ? AND contenido_neto = ?""",
                (datos.nombre.strip(), datos.unidadDeMedida.lower(), float(datos.contenidoNeto))).fetchone()
            if fila is not None:
                return _producto(fila)
            categoria = getattr(datos, "categoria", None) or "Sin clasificar"
            cursor = conexion.execute(
                """INSERT INTO producto (descripcion, categoria, contenido_neto, unidad_medida)
                   VALUES (?, ?, ?, ?)""",
                (datos.nombre.strip(), categoria, float(datos.contenidoNeto), datos.unidadDeMedida.lower()))
            return Producto(datos.nombre.strip(), categoria, float(datos.contenidoNeto),
                            datos.unidadDeMedida.lower(), id=cursor.lastrowid)

    # --- auxiliares -------------------------------------------------------
    @staticmethod
    def _cargarEtiquetas(conexion: sqlite3.Connection, productos: list[Producto], cadena: str | None = None,
                         fechaInicio: date | None = None, fechaFin: date | None = None) -> None:
        if not productos:
            return
        por_id = {p.id: p for p in productos}
        cadenas: dict[int, CadenaDeSupermercados] = {}
        condiciones = [f"e.id_producto IN ({','.join('?' * len(por_id))})"]
        parametros: list = list(por_id)
        if cadena:
            condiciones.append("c.nombre = ?")
            parametros.append(cadena)
        if fechaInicio:
            condiciones.append("e.fecha >= ?")
            parametros.append(fechaInicio.isoformat())
        if fechaFin:
            condiciones.append("e.fecha <= ?")
            parametros.append(fechaFin.isoformat())
        filas = conexion.execute(
            f"""SELECT e.*, c.nombre AS nombre_cadena
                FROM etiqueta_anaquel e JOIN cadena_supermercado c ON c.id_cadena = e.id_cadena
                WHERE {' AND '.join(condiciones)}
                ORDER BY e.fecha""", parametros).fetchall()
        for f in filas:
            cad = cadenas.setdefault(f["id_cadena"], CadenaDeSupermercados(f["nombre_cadena"], id=f["id_cadena"]))
            producto = por_id[f["id_producto"]]
            producto.agregarEtiqueta(EtiquetaDeAnaquel(
                producto, cad, f["precio"], f["precio_promocional"], date.fromisoformat(f["fecha"]),
                pum=f["pum"], id=f["id_etiqueta"]))
