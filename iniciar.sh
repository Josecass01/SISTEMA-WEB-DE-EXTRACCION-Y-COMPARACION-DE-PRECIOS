#!/bin/sh
# Inicia los dos procesos del servicio (Tabla 24 del Manual del sistema):
#  1. el proceso de recolección, que espera la hora programada (CU-S05);
#  2. el servidor web, que atiende las páginas del comprador.
set -e

python -m src.recolector &

exec gunicorn --workers 1 --threads 8 --timeout 60 \
     --bind "0.0.0.0:${PORT:-8000}" src.app:app
