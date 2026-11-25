"""
Agrega sucursales de D1 y Olímpica de las zonas Centro, Manga, Bocagrande,
Pie de la Popa, 19 de Abril y El Bosque, que no estaban registradas.

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
]


def agregar(ruta) -> int:
    agregadas = 0
    with sqlite3.connect(ruta) as conexion:
        cadenas = dict(conexion.execute("SELECT nombre, id_cadena FROM cadena_supermercado"))
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
