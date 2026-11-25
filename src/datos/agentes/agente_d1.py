"""
Agente de D1: la tienda en línea de D1 (domicilios.tiendasd1.com) se arma con
JavaScript, así que se abre con Playwright (Chromium sin interfaz). El agente
escucha las respuestas JSON que recibe la página y toma de ellas los objetos que
tienen nombre y precio; si no encuentra ninguno, lee las tarjetas de la página.
"""

from __future__ import annotations

import logging
from urllib.parse import quote

from .agente_de_supermercado import (TERMINOS_DE_BUSQUEDA, AgenteDeSupermercado, FormatoNoReconocido,
                                     FuenteNoDisponible, ProductoPublicado)
from .conversion import extraerContenido, limpiarPrecio

registro = logging.getLogger(__name__)

URL_BASE = "https://domicilios.tiendasd1.com"
URL_BUSQUEDA = URL_BASE + "/search?name={termino}"
CLAVES_NOMBRE = ("name", "productName", "nombre", "title", "description")
CLAVES_PRECIO = ("price", "precio", "Price", "listPrice", "ListPrice", "sellingPrice")

# Lee de las tarjetas de producto el texto completo (nombre y precio).
_LEER_TARJETAS = """
() => Array.from(document.querySelectorAll('[class*="product" i], [class*="card" i]'))
    .map(e => e.innerText).filter(t => t && t.includes('$') && t.length < 300)
"""


def _buscarProductos(dato, encontrados: list[tuple[str, float]]) -> None:
    """Recorre el JSON y guarda los pares (nombre, precio) que encuentra."""
    if isinstance(dato, dict):
        nombre = next((dato[c] for c in CLAVES_NOMBRE if isinstance(dato.get(c), str)), None)
        precio = next((dato[c] for c in CLAVES_PRECIO if isinstance(dato.get(c), (int, float, str))), None)
        if nombre and precio is not None and limpiarPrecio(precio) > 0:
            encontrados.append((nombre.strip(), limpiarPrecio(precio)))
        for valor in dato.values():
            _buscarProductos(valor, encontrados)
    elif isinstance(dato, list):
        for valor in dato:
            _buscarProductos(valor, encontrados)


class AgenteD1(AgenteDeSupermercado):
    def __init__(self, terminos: list[str] | None = None, tiempoDeEspera: float = 30):
        self._terminos = terminos or TERMINOS_DE_BUSQUEDA
        self._tiempoDeEspera = tiempoDeEspera * 1000

    @property
    def cadena(self) -> str:
        return "D1"

    def obtenerProductos(self) -> list[ProductoPublicado]:
        try:
            from playwright.sync_api import Error as ErrorPlaywright
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise FuenteNoDisponible("Playwright no está instalado") from exc

        pares: list[tuple[str, float]] = []
        paginas_cargadas = 0
        try:
            with sync_playwright() as p:
                navegador = p.chromium.launch(headless=True)
                pagina = navegador.new_page()

                def alResponder(respuesta):
                    if "json" in (respuesta.headers.get("content-type") or ""):
                        try:
                            _buscarProductos(respuesta.json(), pares)
                        except Exception:  # noqa: BLE001 - respuestas ajenas al catálogo
                            pass

                pagina.on("response", alResponder)
                for termino in self._terminos:
                    try:
                        pagina.goto(URL_BUSQUEDA.format(termino=quote(termino)), timeout=self._tiempoDeEspera,
                                    wait_until="networkidle")
                        paginas_cargadas += 1
                        for texto in pagina.evaluate(_LEER_TARJETAS):
                            lineas = [l.strip() for l in texto.splitlines() if l.strip()]
                            nombre = next((l for l in lineas if "$" not in l and extraerContenido(l)), None)
                            precio = next((limpiarPrecio(l) for l in lineas if "$" in l), 0)
                            if nombre and precio:
                                pares.append((nombre, precio))
                    except ErrorPlaywright as exc:
                        registro.warning("D1: error al buscar «%s»: %s", termino, exc)
                navegador.close()
        except ErrorPlaywright as exc:
            raise FuenteNoDisponible(f"no fue posible abrir la tienda de D1: {exc}") from exc

        if paginas_cargadas == 0:
            raise FuenteNoDisponible("domicilios.tiendasd1.com no respondió")

        publicados: dict[str, ProductoPublicado] = {}
        for nombre, precio in pares:
            contenido = extraerContenido(nombre)
            if contenido:
                publicados.setdefault(nombre.lower(), ProductoPublicado(nombre, contenido[0], contenido[1], precio))
        if not publicados:
            raise FormatoNoReconocido("no se reconocieron productos en la tienda de D1")
        return list(publicados.values())
