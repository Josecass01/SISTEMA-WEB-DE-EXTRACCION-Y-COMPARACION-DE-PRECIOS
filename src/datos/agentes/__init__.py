"""Agentes de servicio (SA): uno por cadena (patrón Adaptador, Figura 15)."""

from .agente_ara import AgenteAra
from .agente_d1 import AgenteD1
from .agente_de_supermercado import (AgenteDeSupermercado, FormatoNoReconocido, FuenteNoDisponible,
                                     ProductoPublicado)
from .agente_olimpica import AgenteOlimpica

__all__ = ["AgenteAra", "AgenteD1", "AgenteDeSupermercado", "AgenteOlimpica", "FormatoNoReconocido",
           "FuenteNoDisponible", "ProductoPublicado"]
