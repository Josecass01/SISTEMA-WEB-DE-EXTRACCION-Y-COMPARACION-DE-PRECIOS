"""
Valores de configuración del sistema.

Los valores de negocio corresponden a las decisiones de diseño de la
Tabla 18 del Manual del sistema; la hora de la recolección se define en
la codificación del sistema (Tabla 14, CU-S05).
"""

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Ruta del archivo de la base de datos. En Railway se apunta al volumen
# persistente del servicio con la variable de entorno RUTA_BASE_DE_DATOS.
RUTA_BASE_DE_DATOS = Path(os.environ.get("RUTA_BASE_DE_DATOS", RAIZ / "datos" / "paracompara.db"))

# Base de datos inicial que se copia al volumen la primera vez.
RUTA_BASE_DE_DATOS_INICIAL = RAIZ / "datos_iniciales" / "paracompara.db"

# Tabla 18 del Manual del sistema.
RADIO_DE_COBERTURA_KM = 10
MAXIMO_PRODUCTOS_POR_LISTA = 50
INTERVALO_MAXIMO_HISTORIAL_MESES = 12

# CU-S01, extensión 3a.
MAXIMO_RESULTADOS_BUSQUEDA = 20

# CU-S05: hora de la recolección diaria (hora de Colombia).
HORA_RECOLECCION = os.environ.get("HORA_RECOLECCION", "03:00")
