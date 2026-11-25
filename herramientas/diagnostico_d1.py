"""
Prueba el agente de D1 en una sola categoría y guarda la página tal como la
ve el agente, por si hay que revisar cómo se reconocen las tarjetas.

Uso:  python -m herramientas.diagnostico_d1
Genera datos/d1_muestra.html y datos/d1_muestra.png.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

from src.datos.agentes.agente_d1 import (ESPERA_RENDERIZADO_MS, EXTRAER_TARJETAS,
                                         AgenteD1)

SALIDA = Path("datos")


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    url = "https://www.d1.com.co/lacteos-y-huevos"
    with sync_playwright() as pw:
        navegador = pw.chromium.launch(headless=True)
        pagina = navegador.new_page(locale="es-CO", timezone_id="America/Bogota",
                                    viewport={"width": 1366, "height": 900})
        pagina.goto(url, wait_until="domcontentloaded", timeout=60_000)
        pagina.wait_for_timeout(ESPERA_RENDERIZADO_MS)
        AgenteD1()._cargarTodos(pagina)
        tarjetas = pagina.evaluate(EXTRAER_TARJETAS)
        (SALIDA / "d1_muestra.html").write_text(pagina.content(), encoding="utf-8")
        pagina.screenshot(path=str(SALIDA / "d1_muestra.png"), full_page=False)
        navegador.close()

    convertidos = [AgenteD1._convertir(t["texto"]) for t in tarjetas]
    validos = [c for c in convertidos if c]
    print(f"Tarjetas encontradas: {len(tarjetas)}  |  productos válidos: {len(validos)}")
    for c in validos[:10]:
        print(f"  {c.nombre}  ->  ${c.precio:,}  ({c.contenidoNeto:g} {c.unidadDeMedida})".replace(",", "."))
    print("Página guardada en datos/d1_muestra.html y datos/d1_muestra.png")


if __name__ == "__main__":
    main()
