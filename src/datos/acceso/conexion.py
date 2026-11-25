"""Conexión con la base de datos SQLite y esquema del modelo de persistencia (Figura 16)."""

from __future__ import annotations

import os
import shutil
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from src import configuracion

ESQUEMA = """
CREATE TABLE IF NOT EXISTS producto (
    id_producto     INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion     TEXT    NOT NULL,
    categoria       TEXT    NOT NULL,
    contenido_neto  REAL    NOT NULL CHECK (contenido_neto > 0),
    unidad_medida   TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS cadena_supermercado (
    id_cadena  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre     TEXT    NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS tienda (
    id_tienda  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cadena  INTEGER NOT NULL REFERENCES cadena_supermercado(id_cadena),
    nombre     TEXT    NOT NULL,
    direccion  TEXT    NOT NULL,
    latitud    REAL    NOT NULL,
    longitud   REAL    NOT NULL
);
CREATE TABLE IF NOT EXISTS etiqueta_anaquel (
    id_etiqueta         INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto         INTEGER NOT NULL REFERENCES producto(id_producto),
    id_cadena           INTEGER NOT NULL REFERENCES cadena_supermercado(id_cadena),
    fecha               TEXT    NOT NULL,
    precio              REAL    NOT NULL CHECK (precio > 0),
    precio_promocional  REAL,
    pum                 REAL    NOT NULL,
    UNIQUE (id_producto, id_cadena, fecha)
);
CREATE TABLE IF NOT EXISTS resultado_recoleccion (
    id_resultado          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cadena             INTEGER NOT NULL REFERENCES cadena_supermercado(id_cadena),
    fecha                 TEXT    NOT NULL,
    estado                TEXT    NOT NULL,
    registros_procesados  INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_etiqueta_producto ON etiqueta_anaquel(id_producto, id_cadena, fecha);
CREATE INDEX IF NOT EXISTS idx_tienda_cadena ON tienda(id_cadena);
"""


def obtenerConexion(ruta: Path | None = None) -> sqlite3.Connection:
    conexion = sqlite3.connect(ruta or configuracion.RUTA_BASE_DE_DATOS, timeout=30)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.execute("PRAGMA journal_mode = WAL")  # las lecturas no se bloquean durante la escritura
    return conexion


@contextmanager
def abrir(ruta: Path | None = None):
    """Abre una conexión, confirma la transacción al terminar (o la deshace si falla) y la cierra."""
    conexion = obtenerConexion(ruta)
    try:
        with conexion:
            yield conexion
    finally:
        conexion.close()


def prepararBaseDeDatos(ruta: Path | None = None) -> None:
    """
    Si el archivo de la base de datos no existe (por ejemplo, el volumen recién
    creado en Railway), copia la base de datos inicial; luego asegura el esquema.
    """
    ruta = Path(ruta or configuracion.RUTA_BASE_DE_DATOS)
    if not ruta.exists():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        if configuracion.RUTA_BASE_DE_DATOS_INICIAL.exists():
            # Copia a un archivo temporal y lo renombra, para que el proceso web y el
            # de recolección, que arrancan a la vez, nunca vean una copia a medias.
            temporal = ruta.with_name(f"{ruta.name}.{os.getpid()}.tmp")
            shutil.copyfile(configuracion.RUTA_BASE_DE_DATOS_INICIAL, temporal)
            if ruta.exists():
                temporal.unlink()
            else:
                os.replace(temporal, ruta)
    with abrir(ruta) as conexion:
        conexion.executescript(ESQUEMA)
