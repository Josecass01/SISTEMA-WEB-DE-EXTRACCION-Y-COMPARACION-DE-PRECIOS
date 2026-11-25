"""
Agrega sucursales de Ara, D1 y Olímpica que no estaban registradas
(Centro, Manga, Bocagrande, Pie de la Popa, Crespo, El Bosque y otras zonas).
Los precios de Ara son simulados, pero sus sucursales son reales.

Uso:  python -m herramientas.agregar_sucursales
Actualiza la base de datos inicial (datos_iniciales/paracompara.db) y, si
existe, la base de datos local (datos/paracompara.db), sin borrar los precios.
Si una sucursal ya está registrada con el mismo nombre, no la repite.
"""
import sqlite3

from src import configuracion

SUCURSALES = [
    # (cadena, nombre, dirección, latitud, longitud)
    ("D1", "D1 Manga", "Cl. 26 #21-78, Manga", 10.4129637, -75.5373902),
    ("D1", "D1 Pie de la Popa", "Cl. 30 #21-46, Pie de la Popa", 10.4178443, -75.5297026),
    ("D1", "D1 19 de Abril", "Cl. 30 #45-2 a 45-50, 19 de Abril", 10.4053187, -75.5100715),
    ("D1", "D1 Bocagrande", "Cl. 6 #3-59, Bocagrande", 10.3996990, -75.5562816),
    ("D1", "D1 El Laguito", "Cra. 1 #1A-85, El Laguito", 10.3962441, -75.5634390),
    ("Olímpica", "Olímpica Avenida Sucre", "Cra. 3 #181, Bocagrande", 10.4000836, -75.5572141),
    ("Olímpica", "Olímpica Bocagrande", "Cra. 2 #63-37, Bocagrande", 10.4104220, -75.5508190),
    ("Olímpica", "Olímpica Centro", "Dg. 35 #35, El Centro", 10.4246540, -75.5483962),
    ("Olímpica", "Olímpica Crisanto Luque", "Av. Crisanto Luque #50-06, El Refugio", 10.3939626, -75.5171846),
    ("Ara", "Ara Armenia, El Cairo", "Cl. 30 #49-25, El Cairo", 10.4050201, -75.5074028),
    ("Ara", "Ara Tesca", "Olaya Herrera #50-30, Castillete", 10.4083118, -75.5007163),
    ("Ara", "Ara Escallón Villa", "Cra. 53 #30F-46, Escallón Villa", 10.4032757, -75.4973940),
    ("Ara", "Ara Sevilla", "Cl. 31D #63-96, 13 de Junio", 10.4053940, -75.4862223),
    ("Ara", "Ara El Bosque", "Tv. 51 #21A-28, Alto Bosque", 10.3932162, -75.5203895),
    ("Ara", "Ara Centro", "Calle de la Mantilla #3-32B, La Matuna", 10.4236311, -75.5479095),
    ("Ara", "Ara Manga Calle Real", "Cl. 29A #21A-30, Manga", 10.4138842, -75.5342947),
    ("Ara", "Ara Pie de la Popa", "Cra. 22 #22A-27, Pie de la Popa", 10.4156589, -75.5281374),
    ("Ara", "Ara Bocagrande", "Cra. 3 #6-76, Bocagrande", 10.4006715, -75.5562538),
    ("Ara", "Ara La Plazuela", "Cl. 71 #26-30, Santa Mónica", 10.3886564, -75.4810469),
    ("Ara", "Ara Crespo", "Cl. 70 #4-68, Crespo", 10.4461425, -75.5173621),
]


def agregar(ruta) -> int:
    agregadas = 0
    with sqlite3.connect(ruta) as conexion:
        cadenas = dict(conexion.execute("SELECT nombre, id_cadena FROM cadena_supermercado"))
        # Retira las sucursales de Ara que no están en la lista (versión anterior de este script).
        nombres_ara = [n for c, n, *_ in SUCURSALES if c == "Ara"]
        conexion.execute(
            f"DELETE FROM tienda WHERE id_cadena = ? AND nombre NOT IN ({','.join('?' * len(nombres_ara))})",
            (cadenas["Ara"], *nombres_ara))
        for cadena, nombre, direccion, latitud, longitud in SUCURSALES:
            if conexion.execute("SELECT 1 FROM tienda WHERE nombre = ?", (nombre,)).fetchone():
                continue
            conexion.execute(
                "INSERT INTO tienda (id_cadena, nombre, direccion, latitud, longitud) VALUES (?, ?, ?, ?, ?)",
                (cadenas[cadena], nombre, direccion, latitud, longitud))
            agregadas += 1
    return agregadas


def main() -> None:
    for ruta in (configuracion.RUTA_BASE_DE_DATOS_INICIAL, configuracion.RUTA_BASE_DE_DATOS):
        if ruta.exists():
            print(f"{ruta}: {agregar(ruta)} sucursales agregadas")


if __name__ == "__main__":
    main()
