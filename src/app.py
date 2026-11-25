"""
Punto de entrada del proceso web. Gunicorn lo ejecuta con: gunicorn src.app:app

Para desarrollo local:  python -m src.app
"""

import logging

from src.datos.acceso import prepararBaseDeDatos
from src.presentacion.aplicacion import crearAplicacion

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
prepararBaseDeDatos()
app = crearAplicacion()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
