"""Componentes de acceso a datos (DAC) sobre SQLite (Figura 16)."""

from .cadena_dac import CadenaDAC, EtiquetaDAC, RecoleccionDAC
from .conexion import ESQUEMA, conectar, prepararBaseDeDatos
from .interfaces import ICadenaDAC, IEtiquetaDAC, IProductoDAC, IRecoleccionDAC
from .producto_dac import ProductoDAC

__all__ = ["CadenaDAC", "ESQUEMA", "EtiquetaDAC", "ICadenaDAC", "IEtiquetaDAC", "IProductoDAC",
           "IRecoleccionDAC", "ProductoDAC", "RecoleccionDAC", "conectar", "prepararBaseDeDatos"]
