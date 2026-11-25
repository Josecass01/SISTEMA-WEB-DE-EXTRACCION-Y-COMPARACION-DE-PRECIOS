"""Componentes de acceso a datos (DAC): únicos que conocen la base de datos."""

from .cadena_dac import CadenaDAC
from .conexion import prepararBaseDeDatos
from .etiqueta_dac import EtiquetaDAC
from .interfaces import ICadenaDAC, IEtiquetaDAC, IProductoDAC, IRecoleccionDAC
from .producto_dac import ProductoDAC
from .recoleccion_dac import RecoleccionDAC

__all__ = ["CadenaDAC", "EtiquetaDAC", "ICadenaDAC", "IEtiquetaDAC", "IProductoDAC",
           "IRecoleccionDAC", "ProductoDAC", "RecoleccionDAC", "prepararBaseDeDatos"]
