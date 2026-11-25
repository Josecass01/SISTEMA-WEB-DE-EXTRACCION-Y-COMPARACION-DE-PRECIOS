"""
Interfaz común de los agentes de servicio (Figura 15).

Cada agente convierte el formato propio de su fuente (sitio web o catálogo
simulado) a la estructura común ProductoPublicado (patrón Adaptador). La
recolección invoca obtenerProductos() sin conocer cuál agente la atiende
(polimorfismo y variaciones protegidas).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ProductoPublicado:
    """«estructura» con los datos de un producto tal como lo publica una cadena."""

    nombre: str
    contenidoNeto: float
    unidadDeMedida: str
    precio: float
    precioPromocional: float | None = None


class FormatoNoReconocido(Exception):
    """La fuente cambió de formato de manera drástica (CU-S05, extensión 2b)."""


class FuenteNoDisponible(Exception):
    """La fuente no responde (CU-S05, extensión 2a)."""


class AgenteDeSupermercado(ABC):
    """«interface» AgenteDeSupermercado."""

    #: Nombre de la cadena que atiende el agente, igual al registrado en la base de datos.
    cadena: str = ""

    @abstractmethod
    def obtenerProductos(self) -> list[ProductoPublicado]:
        """Productos y precios publicados por la cadena."""
