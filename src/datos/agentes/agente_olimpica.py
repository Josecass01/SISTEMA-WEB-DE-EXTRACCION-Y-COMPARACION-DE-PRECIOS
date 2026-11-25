"""
Agente de Olímpica: consulta el catálogo público de la tienda en línea
(olimpica.com, plataforma VTEX) con Requests.
"""

from __future__ import annotations

import logging

import requests

from .agente_de_supermercado import (TERMINOS_DE_BUSQUEDA, AgenteDeSupermercado, FormatoNoReconocido,
                                     FuenteNoDisponible, ProductoPublicado)
from .conversion import extraerContenido, limpiarPrecio

registro = logging.getLogger(__name__)

URL_BUSQUEDA = "https://www.olimpica.com/api/catalog_system/pub/products/search"
PRODUCTOS_POR_TERMINO = 30
CABECERAS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ParaCompara/1.0",
             "Accept": "application/json"}


class AgenteOlimpica(AgenteDeSupermercado):
    def __init__(self, terminos: list[str] | None = None, sesion: requests.Session | None = None,
                 tiempoDeEspera: float = 20):
        self._terminos = terminos or TERMINOS_DE_BUSQUEDA
        self._sesion = sesion or requests.Session()
        self._tiempoDeEspera = tiempoDeEspera

    @property
    def cadena(self) -> str:
        return "Olímpica"

    def obtenerProductos(self) -> list[ProductoPublicado]:
        publicados: dict[str, ProductoPublicado] = {}
        respuestas = 0
        for termino in self._terminos:
            try:
                respuesta = self._sesion.get(URL_BUSQUEDA, headers=CABECERAS, timeout=self._tiempoDeEspera,
                                             params={"ft": termino, "_from": 0, "_to": PRODUCTOS_POR_TERMINO - 1})
            except requests.RequestException as exc:
                registro.warning("Olímpica: error al buscar «%s»: %s", termino, exc)
                continue
            if respuesta.status_code not in (200, 206):
                registro.warning("Olímpica: «%s» respondió %s", termino, respuesta.status_code)
                continue
            respuestas += 1
            try:
                items = respuesta.json()
            except ValueError as exc:
                raise FormatoNoReconocido("Olímpica no respondió JSON") from exc
            if not isinstance(items, list):
                raise FormatoNoReconocido("respuesta de Olímpica con formato desconocido")
            for item in items:
                producto = self._convertir(item)
                if producto:
                    publicados.setdefault(producto.nombre.lower(), producto)
        if respuestas == 0:
            raise FuenteNoDisponible("olimpica.com no respondió")
        return list(publicados.values())

    @staticmethod
    def _convertir(item: dict) -> ProductoPublicado | None:
        try:
            nombre = (item.get("productName") or "").strip()
            oferta = item["items"][0]["sellers"][0]["commertialOffer"]
        except (KeyError, IndexError, TypeError, AttributeError):
            return None
        if not oferta.get("IsAvailable", True):
            return None
        contenido = extraerContenido(nombre)
        if not nombre or contenido is None:
            return None
        precio_lista = limpiarPrecio(oferta.get("ListPrice") or oferta.get("Price"))
        precio = limpiarPrecio(oferta.get("Price"))
        promocional = precio if precio and precio_lista and precio < precio_lista else None
        categorias = item.get("categories") or []
        categoria = categorias[0].strip("/").split("/")[-1] if categorias else "Sin clasificar"
        return ProductoPublicado(nombre, contenido[0], contenido[1], precio_lista or precio, promocional,
                                 categoria or "Sin clasificar")
