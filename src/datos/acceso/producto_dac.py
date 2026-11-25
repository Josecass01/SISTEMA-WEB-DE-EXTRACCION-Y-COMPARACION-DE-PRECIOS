"""Componente de acceso a datos de los productos y sus precios (Figura 15)."""

from __future__ import annotations

import difflib
import re
import unicodedata
from datetime import date
from pathlib import Path

from src.negocio.entidades import CadenaDeSupermercados, EtiquetaDeAnaquel, Producto

from .conexion import abrir
from .interfaces import IProductoDAC

SIN_CLASIFICAR = "Sin clasificar"
SIMILITUD_MINIMA_TERMINO = 0.75     # tolerancia a errores tipográficos leves (CU-S01, 2a)
SIMILITUD_MINIMA_PRODUCTO = 0.75    # para reconocer el mismo producto publicado por otra cadena


def normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", " ", sin_tildes.lower())


def palabras(texto: str) -> list[str]:
    """Palabras significativas: letras, de tres o más caracteres."""
    return [p for p in normalizar(texto).split() if len(p) >= 3 and not p.isdigit()]


class ProductoDAC(IProductoDAC):
    def __init__(self, ruta: Path | None = None):
        self._ruta = ruta

    # --- consultas ---------------------------------------------------------
    def buscar(self, termino: str, cadena: str | None) -> list[Producto]:
        """
        Productos cuya descripción contiene las palabras del término, con su
        precio vigente en cada cadena (o solo en la cadena indicada). Si no hay
        coincidencias, busca el término correcto más cercano (CU-S01, 2a).
        """
        buscadas = palabras(termino)
        if not buscadas:
            return []
        with abrir(self._ruta) as conexion:
            filas = conexion.execute(
                "SELECT id_producto, descripcion, categoria, contenido_neto, unidad_medida FROM producto"
            ).fetchall()
            coincidencias = self._filtrar(filas, buscadas)
            if not coincidencias:
                corregidas = self._corregir(filas, buscadas)
                if corregidas != buscadas:
                    coincidencias = self._filtrar(filas, corregidas)
            productos = [self._aProducto(f) for f in coincidencias]
            self._cargarEtiquetasVigentes(conexion, productos, cadena)
        return [p for p in productos if p.obtenerPreciosOrdenadosPorPUM()]

    def buscarPorNombre(self, nombre: str) -> Producto | None:
        """Producto que corresponde al nombre ingresado en la lista de compras."""
        objetivo = normalizar(nombre).split()
        buscadas = palabras(nombre)
        if not buscadas:
            return None
        with abrir(self._ruta) as conexion:
            filas = conexion.execute(
                "SELECT id_producto, descripcion, categoria, contenido_neto, unidad_medida FROM producto"
            ).fetchall()
            exactas = [f for f in filas if normalizar(f["descripcion"]).split() == objetivo]
            candidatas = exactas or self._filtrar(filas, buscadas)
            if not candidatas:
                return None
            productos = [self._aProducto(f) for f in candidatas]
            self._cargarEtiquetasVigentes(conexion, productos, None)
        con_precio = [p for p in productos if p.obtenerPreciosOrdenadosPorPUM()]
        if not con_precio:
            return None
        # Se prefiere el producto disponible en más cadenas y con la descripción más corta.
        return min(con_precio, key=lambda p: (-len(p.obtenerPreciosOrdenadosPorPUM()), len(p.descripcion)))

    def obtenerConHistorial(self, idProducto: int, fechaInicio: date, fechaFin: date) -> Producto | None:
        with abrir(self._ruta) as conexion:
            fila = conexion.execute(
                """SELECT id_producto, descripcion, categoria, contenido_neto, unidad_medida
                   FROM producto WHERE id_producto = ?""", (idProducto,)).fetchone()
            if fila is None:
                return None
            producto = self._aProducto(fila)
            cadenas = self._cadenas(conexion)
            for e in conexion.execute(
                    """SELECT id_etiqueta, id_cadena, fecha, precio, precio_promocional, pum
                       FROM etiqueta_anaquel
                       WHERE id_producto = ? AND fecha BETWEEN ? AND ?
                       ORDER BY fecha""",
                    (idProducto, fechaInicio.isoformat(), fechaFin.isoformat())):
                producto.agregarEtiqueta(self._aEtiqueta(e, producto, cadenas[e["id_cadena"]]))
        return producto

    # --- recolección -------------------------------------------------------
    def obtenerOCrear(self, datos) -> Producto:
        """
        Producto que corresponde a los datos publicados (ProductoPublicado).
        Se reconoce el mismo producto aunque lo publique otra cadena con una
        redacción distinta, siempre que tenga el mismo contenido neto.
        """
        unidad = datos.unidadDeMedida.lower()
        buscadas = set(palabras(datos.nombre))
        with abrir(self._ruta) as conexion:
            filas = conexion.execute(
                """SELECT id_producto, descripcion, categoria, contenido_neto, unidad_medida
                   FROM producto WHERE unidad_medida = ? AND ABS(contenido_neto - ?) < 0.001""",
                (unidad, float(datos.contenidoNeto))).fetchall()
            mejor, mejor_similitud = None, 0.0
            for f in filas:
                if normalizar(f["descripcion"]).split() == normalizar(datos.nombre).split():
                    return self._aProducto(f)
                propias = set(palabras(f["descripcion"]))
                if buscadas and propias:
                    similitud = len(buscadas & propias) / len(buscadas | propias)
                    if similitud > mejor_similitud:
                        mejor, mejor_similitud = f, similitud
            if mejor is not None and mejor_similitud >= SIMILITUD_MINIMA_PRODUCTO:
                return self._aProducto(mejor)
            cursor = conexion.execute(
                """INSERT INTO producto (descripcion, categoria, contenido_neto, unidad_medida)
                   VALUES (?, ?, ?, ?)""", (datos.nombre, SIN_CLASIFICAR, float(datos.contenidoNeto), unidad))
            return Producto(datos.nombre, SIN_CLASIFICAR, float(datos.contenidoNeto), unidad, id=cursor.lastrowid)

    # --- apoyo -------------------------------------------------------------
    @staticmethod
    def _filtrar(filas, buscadas: list[str]):
        return [f for f in filas if all(p in normalizar(f["descripcion"]) for p in buscadas)]

    @staticmethod
    def _corregir(filas, buscadas: list[str]) -> list[str]:
        vocabulario = sorted({p for f in filas for p in palabras(f["descripcion"])})
        corregidas = []
        for p in buscadas:
            cercanas = difflib.get_close_matches(p, vocabulario, n=1, cutoff=SIMILITUD_MINIMA_TERMINO)
            corregidas.append(cercanas[0] if cercanas else p)
        return corregidas

    @staticmethod
    def _aProducto(f) -> Producto:
        return Producto(f["descripcion"], f["categoria"], f["contenido_neto"], f["unidad_medida"],
                        id=f["id_producto"])

    @staticmethod
    def _aEtiqueta(e, producto: Producto, cadena: CadenaDeSupermercados) -> EtiquetaDeAnaquel:
        return EtiquetaDeAnaquel(producto, cadena, e["precio"], e["precio_promocional"],
                                 date.fromisoformat(e["fecha"]), pum=e["pum"], id=e["id_etiqueta"])

    @staticmethod
    def _cadenas(conexion) -> dict[int, CadenaDeSupermercados]:
        return {f["id_cadena"]: CadenaDeSupermercados(f["nombre"], id=f["id_cadena"])
                for f in conexion.execute("SELECT id_cadena, nombre FROM cadena_supermercado")}

    def _cargarEtiquetasVigentes(self, conexion, productos: list[Producto], cadena: str | None) -> None:
        """Agrega a cada producto la etiqueta más reciente de cada cadena."""
        if not productos:
            return
        cadenas = self._cadenas(conexion)
        por_id = {p.id: p for p in productos}
        marcadores = ",".join("?" * len(por_id))
        filtro_cadena, parametros = "", list(por_id)
        if cadena:
            filtro_cadena = "AND e.id_cadena = (SELECT id_cadena FROM cadena_supermercado WHERE nombre = ?)"
            parametros.append(cadena)
        consulta = f"""
            SELECT e.id_etiqueta, e.id_producto, e.id_cadena, e.fecha, e.precio, e.precio_promocional, e.pum
            FROM etiqueta_anaquel e
            JOIN (SELECT id_producto, id_cadena, MAX(fecha) AS fecha FROM etiqueta_anaquel
                  WHERE id_producto IN ({marcadores}) GROUP BY id_producto, id_cadena) v
              ON v.id_producto = e.id_producto AND v.id_cadena = e.id_cadena AND v.fecha = e.fecha
            WHERE 1 = 1 {filtro_cadena}"""
        for e in conexion.execute(consulta, parametros):
            producto = por_id[e["id_producto"]]
            producto.agregarEtiqueta(self._aEtiqueta(e, producto, cadenas[e["id_cadena"]]))
