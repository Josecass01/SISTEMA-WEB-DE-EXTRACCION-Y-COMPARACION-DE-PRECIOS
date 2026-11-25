# Imagen del sistema para el despliegue en Railway (Tabla 22 del Manual del sistema).
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Bogota \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium

COPY src ./src
COPY datos_iniciales ./datos_iniciales
COPY iniciar.sh .
RUN chmod +x iniciar.sh

EXPOSE 8000
CMD ["./iniciar.sh"]
