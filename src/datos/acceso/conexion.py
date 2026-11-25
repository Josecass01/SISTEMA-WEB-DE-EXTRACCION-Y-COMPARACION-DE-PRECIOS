"""Conexión con la base de datos SQLite (modelo de persistencia, Figura 16)."""

from __future__ import annotations

import logging
import shutil
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from src import configuracion

registro = logging.getLogger(__name__)

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


def prepararBaseDeDatos() -> None:
    """
    Deja lista la base de datos: la primera vez copia la base inicial
    (datos_iniciales/paracompara.db); siempre verifica que exista el esquema.
    """
    ruta = configuracion.RUTA_BASE_DE_DATOS
    if not ruta.exists():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        if configuracion.RUTA_BASE_DE_DATOS_INICIAL.exists():
            shutil.copyfile(configuracion.RUTA_BASE_DE_DATOS_INICIAL, ruta)
            registro.info("Base de datos creada a partir de %s", configuracion.RUTA_BASE_DE_DATOS_INICIAL)
    with conectar() as conexion:
        conexion.executescript(ESQUEMA)
        conexion.execute("PRAGMA journal_mode = WAL")

@contextmanager
def conectar() -> Iterator[sqlite3.Connection]:
    """Abre una conexión; confirma la transacción al salir o la deshace si hay un error."""
    # La ruta se lee en cada llamada para respetar cambios en la configuración (pruebas).
    conexion = sqlite3.connect(configuracion.RUTA_BASE_DE_DATOS, timeout=30)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()
