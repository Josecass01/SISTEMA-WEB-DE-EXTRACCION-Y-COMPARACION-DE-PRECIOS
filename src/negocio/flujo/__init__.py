"""Flujo de negocio (BW): recolección diaria de precios, sin intervención del usuario."""

from .programador_de_tareas import ProgramadorDeTareas
from .recoleccion_de_precios import IRecoleccion, RecoleccionDePrecios

__all__ = ["IRecoleccion", "ProgramadorDeTareas", "RecoleccionDePrecios"]
