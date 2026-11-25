"""
Agente de servicio de Olímpica (Figura 15).

El sitio de Olímpica entrega los datos directamente por medio de la interfaz
de búsqueda del catálogo (VTEX); por eso se consulta con requests, sin
navegador (Tabla 22).
"""

from __future__ import annotations

import logging
import random
import time

import requests

from .agente_de_supermercado import (AgenteDeSupermercado, FormatoNoReconocido,
                                     FuenteNoDisponible, ProductoPublicado)
from .conversion import extraerContenido, limpiarNombre, limpiarPrecio

registro = logging.getLogger(__name__)

URL_BUSQUEDA = "https://www.olimpica.com/api/catalog_system/pub/products/search/"
ENCABEZADOS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "es-CO,es;q=0.9",
}
# Términos de la canasta familiar que se consultan cada día.
TERMINOS = [
    "arroz", "aceite", "azucar", "sal", "pasta", "lenteja", "frijol", "harina", "avena",
    "cafe", "chocolate", "panela", "leche", "queso", "mantequilla", "yogur", "huevos",
    "atun", "pollo", "carne", "salchicha", "pan", "galleta", "jugo", "agua", "gaseosa",
    "jabon", "detergente", "papel higienico", "crema dental", "shampoo", "suavizante",
]
TAMANO_PAGINA = 50
PAGINAS_POR_TERMINO = 4


class AgenteOlimpica(AgenteDeSupermercado):
    cadena = "Olímpica"

    def __init__(self, pausa: tuple[float, float] = (1.0, 2.0), sesion: requests.Session | None = None):
        self._pausa = pausa
        self._sesion = sesion or requests.Session()

    def obtenerProductos(self) -> list[ProductoPublicado]:
        publicados: dict[str, ProductoPublicado] = {}
        consultas_exitosas = 0
        respuestas_con_formato = 0
        for termino in TERMINOS:
            for pagina in range(PAGINAS_POR_TERMINO):
                datos = self._consultar(termino, pagina * TAMANO_PAGINA)
                if datos is None:
                    break
                consultas_exitosas += 1
                if not isinstance(datos, list):
                    continue
                if datos and all("productName" in d for d in datos):
                    respuestas_con_formato += 1
                for producto in datos:
                    convertido = self._convertir(producto)
                    if convertido:
                        publicados.setdefault(convertido.nombre.lower(), convertido)
                if len(datos) < TAMANO_PAGINA:
                    break
                time.sleep(random.uniform(*self._pausa))
        if consultas_exitosas == 0:
            raise FuenteNoDisponible("El sitio de Olímpica no respondió.")
        if respuestas_con_formato == 0:
            raise FormatoNoReconocido("Las respuestas de Olímpica no tienen el formato esperado.")
        return list(publicados.values())

    def _consultar(self, termino: str, desde: int):
        try:
            r = self._sesion.get(URL_BUSQUEDA, headers=ENCABEZADOS, timeout=25, params={
                "ft": termino, "_from": desde, "_to": desde + TAMANO_PAGINA - 1})
        except requests.RequestException as exc:
            registro.warning("Olímpica no respondió para '%s': %s", termino, exc)
            return None
        if r.status_code not in (200, 206):
            registro.warning("Olímpica respondió HTTP %s para '%s'", r.status_code, termino)
            return None
        try:
            return r.json()
        except ValueError:
            return {}

    @staticmethod
    def _convertir(producto: dict) -> ProductoPublicado | None:
        nombre = limpiarNombre(producto.get("productName", ""))
        contenido = extraerContenido(nombre)
        oferta = {}
        for item in producto.get("items", []):
            for vendedor in item.get("sellers", []):
                oferta = vendedor.get("commertialOffer", {}) or {}
                if oferta.get("Price"):
                    break
            if oferta.get("Price"):
                break
        precio_venta = limpiarPrecio(oferta.get("Price"))
        precio_lista = limpiarPrecio(oferta.get("ListPrice")) or precio_venta
        if not nombre or not contenido or not precio_lista:
            return None
        promocional = precio_venta if precio_venta and precio_venta < precio_lista else None
        return ProductoPublicado(nombre, contenido[0], contenido[1], precio_lista, promocional)
