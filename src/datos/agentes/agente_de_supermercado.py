"""Interfaz común de los agentes de servicio (patrón Adaptador, Figura 15)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class FuenteNoDisponible(Exception):
    """La fuente de la cadena no respondió (CU-S05, extensión 2a)."""


class FormatoNoReconocido(Exception):
    """La fuente respondió con un formato que el agente no reconoce (CU-S05, extensión 2b)."""


@dataclass
class ProductoPublicado:
    """Producto tal como lo publica la cadena, ya convertido a datos del sistema."""

    nombre: str
    contenidoNeto: float
    unidadDeMedida: str
    precio: float
    precioPromocional: float | None = None
    categoria: str = "Sin clasificar"


class AgenteDeSupermercado(ABC):
    """Adapta la fuente de una cadena a la lista de productos publicados."""

    @property
    @abstractmethod
    def cadena(self) -> str: ...

    @abstractmethod
    def obtenerProductos(self) -> list[ProductoPublicado]: ...


# Términos de la canasta familiar que se consultan en las cadenas con búsqueda en línea.
TERMINOS_DE_BUSQUEDA = [
    "arroz", "aceite", "azucar", "sal", "panela", "cafe", "chocolate", "leche", "queso", "mantequilla",
    "margarina", "yogurt", "huevos", "pan tajado", "pasta", "lenteja", "frijol", "garbanzo", "arveja",
    "harina", "avena", "atun", "pollo", "carne", "salchicha", "mortadela", "jabon", "detergente",
    "papel higienico", "crema dental", "blanqueador", "agua", "jugo", "galletas",
]
