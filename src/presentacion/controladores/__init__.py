"""Controladores: uno por caso de uso del usuario comprador (patrón Controlador)."""

from .ctrl_comparacion import CtrlComparacion
from .ctrl_historial import CtrlHistorial
from .ctrl_lista_de_compras import CtrlListaDeCompras
from .ctrl_tiendas_cercanas import CtrlTiendasCercanas

__all__ = ["CtrlComparacion", "CtrlHistorial", "CtrlListaDeCompras", "CtrlTiendasCercanas"]
