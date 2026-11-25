"""
Agente de servicio de D1 (Figura 15).

El sitio de domicilios de D1 genera los precios con JavaScript; por eso se
recorre con navegación automatizada (Playwright y Chromium, Tabla 22).
"""

from __future__ import annotations

import logging
import random
import time

from bs4 import BeautifulSoup

from .agente_de_supermercado import (AgenteDeSupermercado, FormatoNoReconocido,
                                     FuenteNoDisponible, ProductoPublicado)
from .conversion import extraerContenido, limpiarNombre, limpiarPrecio

registro = logging.getLogger(__name__)

URLS_CATEGORIAS = [
    "https://domicilios.tiendasd1.com/ca/lacteos/L%C3%81CTEOS",
    "https://domicilios.tiendasd1.com/ca/alimentos%20y%20despensa/ALIMENTOS%20Y%20DESPENSA",
    "https://domicilios.tiendasd1.com/ca/bebidas/BEBIDAS",
    "https://domicilios.tiendasd1.com/ca/aseo%20hogar/ASEO%20HOGAR",
    "https://domicilios.tiendasd1.com/ca/aseo%20y%20cuidado%20personal/ASEO%20Y%20CUIDADO%20PERSONAL",
    "https://domicilios.tiendasd1.com/ca/congelados/CONGELADOS",
]
SELECTOR_PRODUCTO = "[class*='product-card']"
SELECTOR_NOMBRE = "h3[class*='prod__name']"
SELECTOR_PRECIO = "p[class*='base__price']"
ESPERA_RENDERIZADO_MS = 6000
MAXIMO_PAGINAS = 15


class AgenteD1(AgenteDeSupermercado):
    cadena = "D1"

    def __init__(self, pausa: tuple[float, float] = (1.5, 3.0)):
        self._pausa = pausa

    def obtenerProductos(self) -> list[ProductoPublicado]:
        from playwright.sync_api import Error as ErrorPlaywright
        from playwright.sync_api import sync_playwright

        publicados: dict[str, ProductoPublicado] = {}
        paginas_cargadas = 0
        tarjetas_encontradas = 0
        with sync_playwright() as pw:
            navegador = pw.chromium.launch(
                headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            contexto = navegador.new_context(locale="es-CO", timezone_id="America/Bogota")
            contexto.route("**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf,mp4}",
                           lambda ruta: ruta.abort())
            pagina = contexto.new_page()
            for url_categoria in URLS_CATEGORIAS:
                for numero in range(1, MAXIMO_PAGINAS + 1):
                    url = url_categoria if numero == 1 else f"{url_categoria}?currentPage={numero}"
                    try:
                        pagina.goto(url, wait_until="domcontentloaded", timeout=40_000)
                        pagina.wait_for_timeout(ESPERA_RENDERIZADO_MS)
                        pagina.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        pagina.wait_for_timeout(1500)
                    except ErrorPlaywright as exc:
                        registro.warning("D1 no respondió en %s: %s", url, exc)
                        break
                    paginas_cargadas += 1
                    tarjetas = BeautifulSoup(pagina.content(), "html.parser").select(SELECTOR_PRODUCTO)
                    if not tarjetas:
                        break
                    tarjetas_encontradas += len(tarjetas)
                    for tarjeta in tarjetas:
                        convertido = self._convertir(tarjeta)
                        if convertido:
                            publicados.setdefault(convertido.nombre.lower(), convertido)
                    if len(tarjetas) < 20:
                        break
                    time.sleep(random.uniform(*self._pausa))
            navegador.close()
        if paginas_cargadas == 0:
            raise FuenteNoDisponible("El sitio de D1 no respondió.")
        if tarjetas_encontradas == 0:
            raise FormatoNoReconocido("No se encontraron productos con los selectores de D1.")
        return list(publicados.values())

    @staticmethod
    def _convertir(tarjeta) -> ProductoPublicado | None:
        nodo_nombre = tarjeta.select_one(SELECTOR_NOMBRE)
        nodo_precio = tarjeta.select_one(SELECTOR_PRECIO)
        if not nodo_nombre or not nodo_precio:
            return None
        nombre = limpiarNombre(nodo_nombre.get_text(strip=True))
        precio = limpiarPrecio(nodo_precio.get("content") or nodo_precio.get_text())
        contenido = extraerContenido(nombre)
        if not nombre or not precio or not contenido:
            return None
        return ProductoPublicado(nombre, contenido[0], contenido[1], precio, None)
