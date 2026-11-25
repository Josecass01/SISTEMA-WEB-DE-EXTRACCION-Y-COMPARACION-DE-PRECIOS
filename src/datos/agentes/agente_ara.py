"""
Agente de Ara (precios simulados).

Ara no publica precios en línea; el agente lee el catálogo de productos de la
canasta familiar (catalogo_ara.json), cuyo precio de referencia es el promedio
de los precios de D1 y Olímpica, y aplica cada día una variación de ±3 %.
La variación depende solo de la fecha y del producto, así que es estable en el día.
"""

from __future__ import annotations

import json
import random
from datetime import date
from pathlib import Path

from .agente_de_supermercado import AgenteDeSupermercado, FormatoNoReconocido, ProductoPublicado

RUTA_CATALOGO = Path(__file__).resolve().parent / "catalogo_ara.json"
VARIACION_MAXIMA = 0.03


class AgenteAra(AgenteDeSupermercado):
    def __init__(self, fecha: date | None = None, rutaCatalogo: Path = RUTA_CATALOGO):
        self._fecha = fecha
        self._rutaCatalogo = rutaCatalogo

    @property
    def cadena(self) -> str:
        return "Ara"

    def obtenerProductos(self) -> list[ProductoPublicado]:
        fecha = self._fecha or date.today()
        try:
            catalogo = json.loads(self._rutaCatalogo.read_text(encoding="utf-8"))
            productos = catalogo["productos"]
        except (OSError, ValueError, KeyError) as exc:
            raise FormatoNoReconocido(f"catálogo de Ara no válido: {exc}") from exc

        publicados = []
        for p in productos:
            azar = random.Random(f"{fecha.isoformat()}|{p['descripcion']}")
            variacion = azar.uniform(-VARIACION_MAXIMA, VARIACION_MAXIMA)
            precio = int(round(p["precioReferencia"] * (1 + variacion) / 10.0) * 10)
            publicados.append(ProductoPublicado(p["descripcion"], p["contenidoNeto"], p["unidadDeMedida"],
                                                precio, None, p.get("categoria", "Sin clasificar")))
        return publicados
