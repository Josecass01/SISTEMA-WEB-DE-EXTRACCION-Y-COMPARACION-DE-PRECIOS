"""
Agente de servicio de Ara (Figura 15).

Los precios de Ara son simulados (alcance del sistema): el agente lee el
catálogo simulado de productos de la canasta familiar colombiana, cuyos
precios de referencia corresponden al promedio de los precios de D1 y
Olímpica para el mismo producto, y aplica una variación diaria pequeña.
Para el resto del sistema no hay diferencia con los demás agentes, porque
entrega la misma estructura (ProductoPublicado) por la misma interfaz.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

from .agente_de_supermercado import AgenteDeSupermercado, FormatoNoReconocido, ProductoPublicado

RUTA_CATALOGO = Path(__file__).with_name("catalogo_ara.json")
VARIACION_MAXIMA = 0.03  # ±3 % diario sobre el precio de referencia


class AgenteAra(AgenteDeSupermercado):
    cadena = "Ara"

    def __init__(self, rutaCatalogo: Path = RUTA_CATALOGO, fecha: date | None = None):
        self._rutaCatalogo = rutaCatalogo
        self._fecha = fecha

    def obtenerProductos(self) -> list[ProductoPublicado]:
        try:
            catalogo = json.loads(self._rutaCatalogo.read_text(encoding="utf-8"))
            productos = catalogo["productos"]
        except (OSError, ValueError, KeyError) as exc:
            raise FormatoNoReconocido(f"No se pudo leer el catálogo simulado de Ara: {exc}") from exc
        fecha = self._fecha or date.today()
        publicados = []
        for p in productos:
            precio = self._precioDelDia(p["descripcion"], float(p["precioReferencia"]), fecha)
            publicados.append(ProductoPublicado(
                p["descripcion"], float(p["contenidoNeto"]), p["unidadDeMedida"], precio, None))
        return publicados

    @staticmethod
    def _precioDelDia(descripcion: str, referencia: float, fecha: date) -> int:
        """Variación determinística: el mismo producto y la misma fecha dan el mismo precio."""
        semilla = hashlib.sha256(f"{descripcion}|{fecha.isoformat()}".encode()).digest()
        fraccion = int.from_bytes(semilla[:4], "big") / 0xFFFFFFFF  # 0..1
        variacion = (fraccion * 2 - 1) * VARIACION_MAXIMA
        return int(round(referencia * (1 + variacion) / 10.0) * 10)
