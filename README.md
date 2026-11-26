# Sistema web de extracción y comparación de precios

Proyecto final de **Ingeniería de Software**, Universidad de Cartagena.
Profesor: Martín Monroy.

Integrantes:

- José Luis Castellanos Guardia
- Dayin Heredia
- Daniel Almanza

El sistema recolecta cada día los precios que publican las cadenas **Ara**, **D1** y **Olímpica**
en Cartagena y le permite al comprador:

1. Comparar el precio de un producto entre las cadenas, ordenado por precio por unidad de medida (CU-S01).
2. Evaluar el costo total de su lista de compras en cada cadena (CU-S02).
3. Consultar el historial de precios de un producto (CU-S03).
4. Ubicar las sucursales cercanas a su posición (CU-S04).

La recolección (CU-S05) se ejecuta sola, todos los días, a la hora definida en `src/configuracion.py`.

> **Los precios de Ara son simulados.** Ara no publica precios en línea, así que el agente de Ara
> lee un catálogo de productos de la canasta familiar (`src/datos/agentes/catalogo_ara.json`) cuyo
> precio de referencia es el promedio de los precios de D1 y Olímpica. Cada día aplica una variación
> de ±3 %.

## Organización del código

El código sigue la arquitectura documentada en el Manual del sistema (Figura 22):

| Capa (Manual) | Carpeta | Contenido |
|---|---|---|
| Presentación: páginas (BC) | `src/presentacion/paginas/` | Plantillas HTML, estilos y JavaScript de las cuatro pantallas |
| Presentación: controladores (BW) | `src/presentacion/controladores/` | Un controlador por cada caso de uso del comprador |
| Negocio: entidades (BE) | `src/negocio/entidades/` | Clases del modelo de diseño (Figura 13) |
| Negocio: componentes | `src/negocio/componentes/` | Comparación, lista de compras, historial y ubicación |
| Negocio: flujo | `src/negocio/flujo/` | Recolección de precios y programador de tareas |
| Datos: acceso (DAC) | `src/datos/acceso/` | Acceso a la base de datos SQLite (modelo de la Figura 16) |
| Datos: agentes de servicio (SA) | `src/datos/agentes/` | Un agente por cadena (patrón Adaptador, Figura 15) |

Otros archivos:

- `src/app.py`: punto de entrada del servidor web.
- `src/recolector.py`: punto de entrada del proceso de recolección.
- `datos_iniciales/paracompara.db`: base de datos con la que arranca el sistema.
- `herramientas/migrar_base_anterior.py`: script que generó la base de datos inicial a partir de la versión anterior del proyecto.
- `pruebas/`: pruebas automáticas.
- `Dockerfile` e `iniciar.sh`: empaquetado y arranque para el despliegue.

## Ejecutar en el computador (Windows)

Requisitos: Python 3.13 y Git.

```powershell
git clone <URL del repositorio>
cd <carpeta del repositorio>
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
playwright install chromium
```

Iniciar el sitio web (queda en http://127.0.0.1:8000):

```powershell
python -m src.app
```

Ejecutar una recolección de precios inmediata (en otra terminal, con el entorno activado):

```powershell
python -m src.recolector --ahora
```

La primera vez, el sistema copia `datos_iniciales/paracompara.db` a `datos/paracompara.db`;
la carpeta `datos/` no se sube a GitHub.

Ejecutar las pruebas:

```powershell
python -m pytest pruebas
```

## Despliegue en Railway

El servicio se construye con el `Dockerfile` del repositorio. Al iniciar, `iniciar.sh` arranca el
proceso de recolección y el servidor web (Gunicorn) en el mismo servicio, porque los dos comparten
la base de datos del volumen.

1. Crear la cuenta en [railway.com](https://railway.com) con GitHub y completar la verificación de la cuenta
   (sin ella, el plan de prueba no permite que el servicio salga a internet y la recolección falla).
2. **New Project → Deploy from GitHub repo** y elegir este repositorio.
3. En el servicio, **Volumes → Add volume** con la ruta de montaje `/app/datos`.
4. En **Variables**, agregar:
   - `RUTA_BASE_DE_DATOS` = `/app/datos/paracompara.db`
   - `CLAVE_SESION` = una cadena larga y aleatoria
5. En **Settings → Networking → Generate Domain** para obtener la dirección pública (HTTPS).

Cada `git push` a la rama principal vuelve a desplegar el servicio. Los datos del volumen se conservan.

Variables opcionales:

| Variable | Valor por defecto | Uso |
|---|---|---|
| `HORA_RECOLECCION` | `03:00` | Hora diaria de la recolección (hora de Colombia) |
| `PORT` | `8000` | Puerto del servidor web (Railway lo asigna) |

## Tecnologías

Python 3.13, Flask 3.1, Gunicorn 23, SQLite, Requests (Olímpica),
Playwright con Chromium (D1), schedule (programador de tareas), Chart.js 4.4 (gráfica del historial)
y Docker.
