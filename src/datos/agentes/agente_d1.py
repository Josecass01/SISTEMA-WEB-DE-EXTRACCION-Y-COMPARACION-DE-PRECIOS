"""
Agente de servicio de D1 (Figura 15).

El sitio de D1 (www.d1.com.co) genera los productos y sus precios con
JavaScript; por eso se recorre con navegación automatizada (Playwright y
Chromium, Tabla 22). Cada tarjeta se reconoce por su enlace al producto
(dirección terminada en /p) y por el precio en pesos que contiene, y no por
nombres de clases, que el sitio cambia con frecuencia.
"""

from __future__ import annotations

import logging
import random
import re
import time

from .agente_de_supermercado import (AgenteDeSupermercado, FormatoNoReconocido,
                                     FuenteNoDisponible, ProductoPublicado)
from .conversion import extraerContenido, limpiarNombre, limpiarPrecio

registro = logging.getLogger(__name__)

URLS_CATEGORIAS = [
    "https://www.d1.com.co/despensa",
    "https://www.d1.com.co/lacteos-y-huevos",
    "https://www.d1.com.co/bebidas",
    "https://www.d1.com.co/pollo-carne-y-pescado",
    "https://www.d1.com.co/hogar/aseo-y-limpieza",
    "https://www.d1.com.co/cuidado-personal-y-belleza",
]
ESPERA_RENDERIZADO_MS = 6000
MAXIMO_CLICS_VER_MAS = 30

# Devuelve el texto de cada tarjeta de producto visible en la página.
EXTRAER_TARJETAS = """
() => {
  const vistos = new Set(), tarjetas = [];
  for (const enlace of document.querySelectorAll("a[href*='/p']")) {
    const url = enlace.href.split('?')[0];
    if (!/\\/p$/.test(url) || vistos.has(url)) continue;
    let nodo = enlace;
    for (let i = 0; i < 8 && nodo && !/\\$\\s?[\\d.]+/.test(nodo.innerText || ''); i++) nodo = nodo.parentElement;
    if (!nodo) continue;
    vistos.add(url);
    tarjetas.push({ url: url, texto: nodo.innerText });
  }
  return tarjetas;
}
"""
PRECIO = re.compile(r"\$\s?([\d.]+)")
TEXTOS_IGNORADOS = {"agregar", "+ agregar", "ver más productos"}


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
            contexto = navegador.new_context(locale="es-CO", timezone_id="America/Bogota",
                                             viewport={"width": 1366, "height": 900})
            contexto.route("**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf,mp4}",
                           lambda ruta: ruta.abort())
            pagina = contexto.new_page()
            for url_categoria in URLS_CATEGORIAS:
                try:
                    pagina.goto(url_categoria, wait_until="domcontentloaded", timeout=60_000)
                    pagina.wait_for_timeout(ESPERA_RENDERIZADO_MS)
                    self._cargarTodos(pagina)
                    tarjetas = pagina.evaluate(EXTRAER_TARJETAS)
                except ErrorPlaywright as exc:
                    registro.warning("D1 no respondió en %s: %s", url_categoria, exc)
                    continue
                paginas_cargadas += 1
                tarjetas_encontradas += len(tarjetas)
                registro.info("D1 %s: %d tarjetas", url_categoria, len(tarjetas))
                for tarjeta in tarjetas:
                    convertido = self._convertir(tarjeta["texto"])
                    if convertido:
                        publicados.setdefault(convertido.nombre.lower(), convertido)
                time.sleep(random.uniform(*self._pausa))
            navegador.close()
        if paginas_cargadas == 0:
            raise FuenteNoDisponible("El sitio de D1 no respondió.")
        if tarjetas_encontradas == 0:
            raise FormatoNoReconocido("No se encontraron tarjetas de producto en el sitio de D1.")
        return list(publicados.values())

    def _cargarTodos(self, pagina) -> None:
        """Pulsa «Ver más productos» hasta que la categoría muestre todos sus productos."""
        for _ in range(MAXIMO_CLICS_VER_MAS):
            boton = pagina.get_by_text("Ver más productos", exact=False)
            if boton.count() == 0 or not boton.first.is_visible():
                return
            boton.first.scroll_into_view_if_needed()
            boton.first.click()
            pagina.wait_for_timeout(2500)

    @staticmethod
    def _convertir(texto: str) -> ProductoPublicado | None:
        """
        Del texto de una tarjeta (marca, nombre, precio y botón) obtiene el nombre,
        el contenido neto y el precio. Si la tarjeta muestra dos precios, el mayor es
        el precio regular y el menor el promocional.
        """
        lineas = [l.strip() for l in (texto or "").splitlines() if l.strip()]
        precios = [limpiarPrecio(m) for l in lineas for m in PRECIO.findall(l)]
        precios = [p for p in precios if p]
        candidatas = [l for l in lineas
                      if "$" not in l and l.lower() not in TEXTOS_IGNORADOS and extraerContenido(l)]
        if not precios or not candidatas:
            return None
        nombre = limpiarNombre(max(candidatas, key=len))
        contenido = extraerContenido(nombre)
        if not nombre or not contenido:
            return None
        precio, minimo = max(precios), min(precios)
        return ProductoPublicado(nombre, contenido[0], contenido[1], precio,
                                 minimo if minimo < precio else None)
