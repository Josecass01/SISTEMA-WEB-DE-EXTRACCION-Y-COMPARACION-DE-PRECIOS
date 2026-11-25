"""
Construye la base de datos inicial del sistema (datos_iniciales/paracompara.db)
a partir de la base de datos de la versión anterior del código, y genera el
catálogo simulado de Ara.

Uso:
    python -m herramientas.migrar_base_anterior RUTA_BASE_ANTERIOR

Qué hace:
  1. Crea el esquema del modelo de persistencia (Figura 16).
  2. Registra las cadenas del alcance: Ara, D1 y Olímpica.
  3. Copia las sucursales de D1 y Olímpica, y los productos y precios de esas
     dos cadenas. Los precios de otras cadenas (Éxito, Jumbo) no se copian.
  4. Genera el catálogo simulado de Ara con los productos de la canasta familiar
     que D1 y Olímpica publicaron en la última fecha y cuyos precios son
     consistentes entre sí; el precio de referencia es el promedio de los dos.
  5. Registra los precios simulados de Ara en las mismas fechas del historial.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.datos.acceso.conexion import ESQUEMA  # noqa: E402
from src.datos.agentes.agente_ara import RUTA_CATALOGO, AgenteAra  # noqa: E402
from src.datos.agentes.conversion import extraerContenido  # noqa: E402
from src.negocio.entidades import CadenaDeSupermercados, Producto  # noqa: E402

DESTINO = RAIZ / "datos_iniciales" / "paracompara.db"
CADENAS_ANTERIORES = {"d1": "D1", "olimpica": "Olímpica"}
RELACION_MAXIMA_CONSISTENTE = 1.5  # el precio mayor no supera 1,5 veces el menor
# Productos de la canasta familiar colombiana: la descripción empieza por uno de estos términos.
CANASTA_FAMILIAR = [
    "arroz", "aceite", "azucar", "sal de mesa", "panela", "cafe", "chocolate", "leche", "queso",
    "mantequilla", "margarina", "yogur", "huevo", "pan tajado", "pasta", "lenteja", "frijol",
    "garbanzo", "arveja", "harina", "avena", "atun", "pechuga", "pollo", "carne", "salchicha",
    "mortadela", "jabon", "detergente", "papel higienico", "crema dental", "blanqueador",
    "agua", "jugo", "galleta", "maiz", "papa", "tomate", "cebolla", "platano",
]


def es_de_la_canasta(descripcion: str) -> bool:
    import unicodedata
    texto = unicodedata.normalize("NFKD", descripcion).encode("ascii", "ignore").decode().lower().strip()
    return any(texto.startswith(termino) for termino in CANASTA_FAMILIAR)


def migrar(ruta_anterior: Path) -> None:
    anterior = sqlite3.connect(ruta_anterior)
    anterior.row_factory = sqlite3.Row
    if DESTINO.exists():
        DESTINO.unlink()
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    nueva = sqlite3.connect(DESTINO)
    nueva.row_factory = sqlite3.Row
    nueva.executescript(ESQUEMA)

    cadenas = {}
    for nombre in ("Ara", "D1", "Olímpica"):
        cur = nueva.execute("INSERT INTO cadena_supermercado (nombre) VALUES (?)", (nombre,))
        cadenas[nombre] = CadenaDeSupermercados(nombre, id=cur.lastrowid)

    for s in anterior.execute(
            "SELECT tienda_id, nombre, direccion, lat, lng FROM sucursales WHERE tienda_id IN ('d1','olimpica')"):
        nueva.execute("""INSERT INTO tienda (id_cadena, nombre, direccion, latitud, longitud)
                         VALUES (?, ?, ?, ?, ?)""",
                      (cadenas[CADENAS_ANTERIORES[s["tienda_id"]]].id, s["nombre"], s["direccion"],
                       s["lat"], s["lng"]))

    productos: dict[int, Producto] = {}
    filas = anterior.execute("""
        SELECT p.id, p.nombre, COALESCE(c.nombre, 'Sin clasificar') AS categoria, p.cantidad, p.unidad
        FROM productos p LEFT JOIN categorias c ON c.id = p.categoria_id
        WHERE p.cantidad > 0 AND p.id IN (SELECT producto_id FROM precios WHERE tienda_id IN ('d1','olimpica'))
        ORDER BY p.id""").fetchall()
    for f in filas:
        # El contenido neto se vuelve a obtener del nombre publicado, con la misma
        # depuración que aplican los agentes; si el nombre no lo indica, se conserva el anterior.
        contenido, unidad = extraerContenido(f["nombre"]) or (f["cantidad"], f["unidad"])
        cur = nueva.execute("""INSERT INTO producto (descripcion, categoria, contenido_neto, unidad_medida)
                               VALUES (?, ?, ?, ?)""", (f["nombre"], f["categoria"], contenido, unidad))
        productos[f["id"]] = Producto(f["nombre"], f["categoria"], contenido, unidad, id=cur.lastrowid)

    for pr in anterior.execute(
            "SELECT producto_id, tienda_id, precio, fecha FROM precios WHERE tienda_id IN ('d1','olimpica')"):
        producto = productos.get(pr["producto_id"])
        if producto is None or pr["precio"] <= 0:
            continue
        etiqueta = cadenas[CADENAS_ANTERIORES[pr["tienda_id"]]].registrarPrecio(
            producto, pr["precio"], None, date.fromisoformat(pr["fecha"]))
        nueva.execute("""INSERT OR REPLACE INTO etiqueta_anaquel
                         (id_producto, id_cadena, fecha, precio, precio_promocional, pum)
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      (producto.id, etiqueta.cadena.id, etiqueta.fecha.isoformat(), etiqueta.precio,
                       None, etiqueta.pum))

    # Catálogo simulado de Ara.
    ultima = nueva.execute("SELECT MAX(fecha) FROM etiqueta_anaquel").fetchone()[0]
    catalogo = []
    for f in nueva.execute("""
            SELECT p.id_producto, p.descripcion, p.categoria, p.contenido_neto, p.unidad_medida,
                   MIN(e.precio) AS menor, MAX(e.precio) AS mayor, AVG(e.precio) AS promedio
            FROM producto p JOIN etiqueta_anaquel e ON e.id_producto = p.id_producto
            WHERE e.fecha = ? AND e.id_cadena IN (?, ?)
            GROUP BY p.id_producto HAVING COUNT(DISTINCT e.id_cadena) = 2
            ORDER BY p.categoria, p.descripcion""", (ultima, cadenas["D1"].id, cadenas["Olímpica"].id)):
        if es_de_la_canasta(f["descripcion"]) and f["mayor"] <= f["menor"] * RELACION_MAXIMA_CONSISTENTE:
            catalogo.append({
                "descripcion": f["descripcion"],
                "categoria": f["categoria"],
                "contenidoNeto": f["contenido_neto"],
                "unidadDeMedida": f["unidad_medida"],
                "precioReferencia": int(round(f["promedio"] / 10.0) * 10),
            })
    RUTA_CATALOGO.write_text(json.dumps({
        "descripcion": "Catálogo simulado de Ara: productos de la canasta familiar colombiana. "
                       "El precio de referencia es el promedio de los precios de D1 y Olímpica "
                       f"del {ultima} para el mismo producto.",
        "fechaReferencia": ultima,
        "productos": catalogo,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # Precios simulados de Ara en las fechas del historial.
    por_descripcion = {(p.descripcion, p.unidadDeMedida, float(p.contenidoNeto)): p for p in productos.values()}
    fechas = [r[0] for r in nueva.execute("SELECT DISTINCT fecha FROM etiqueta_anaquel ORDER BY fecha")]
    for texto_fecha in fechas:
        for publicado in AgenteAra(fecha=date.fromisoformat(texto_fecha)).obtenerProductos():
            producto = por_descripcion[(publicado.nombre, publicado.unidadDeMedida, float(publicado.contenidoNeto))]
            etiqueta = cadenas["Ara"].registrarPrecio(producto, publicado.precio, None,
                                                      date.fromisoformat(texto_fecha))
            nueva.execute("""INSERT OR REPLACE INTO etiqueta_anaquel
                             (id_producto, id_cadena, fecha, precio, precio_promocional, pum)
                             VALUES (?, ?, ?, ?, ?, ?)""",
                          (producto.id, etiqueta.cadena.id, texto_fecha, etiqueta.precio, None, etiqueta.pum))

    nueva.commit()
    resumen = {t: nueva.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
               for t in ("cadena_supermercado", "tienda", "producto", "etiqueta_anaquel")}
    nueva.execute("VACUUM")
    nueva.close()
    print(f"Base de datos inicial: {DESTINO}")
    for tabla, total in resumen.items():
        print(f"  {tabla:<20} {total:>6}")
    print(f"Catálogo simulado de Ara: {len(catalogo)} productos ({RUTA_CATALOGO})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python -m herramientas.migrar_base_anterior RUTA_BASE_ANTERIOR")
    migrar(Path(sys.argv[1]))
