"""
Punto de entrada del proceso de recolección (CU-S05).

    python -m src.recolector            espera la hora definida y recolecta cada día
    python -m src.recolector --ahora    ejecuta una recolección inmediata y termina
"""

import argparse
import logging

from src.datos.acceso import prepararBaseDeDatos
from src.negocio.flujo import ProgramadorDeTareas, RecoleccionDePrecios

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main() -> None:
    argumentos = argparse.ArgumentParser(description="Recolección diaria de precios")
    argumentos.add_argument("--ahora", action="store_true", help="recolecta inmediatamente y termina")
    opciones = argumentos.parse_args()
    prepararBaseDeDatos()
    if opciones.ahora:
        RecoleccionDePrecios().ejecutar()
    else:
        ProgramadorDeTareas().iniciar()


if __name__ == "__main__":
    main()
