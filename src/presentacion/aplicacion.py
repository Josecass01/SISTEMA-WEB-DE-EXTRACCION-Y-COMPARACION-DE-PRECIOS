"""
Aplicación web (Flask). Recibe las peticiones del navegador y las entrega al
controlador del caso de uso correspondiente. Flask solo se usa en la capa de
presentación.
"""

from __future__ import annotations

import os
import secrets
import threading
import time
import uuid

from flask import Flask, jsonify, redirect, request, session, url_for

from src.negocio.componentes import EvaluacionDeLista

from .controladores import CtrlComparacion, CtrlHistorial, CtrlListaDeCompras, CtrlTiendasCercanas

DIRECTORIO_PAGINAS = os.path.join(os.path.dirname(__file__), "paginas")
DURACION_LISTA_SEGUNDOS = 4 * 3600


class ListasEnMemoria:
    """
    Listas de compras de los usuarios mientras las evalúan. La lista no se
    almacena en la base de datos (sección 3.2.2 del Manual del sistema).
    """

    def __init__(self):
        self._listas: dict[str, tuple[EvaluacionDeLista, float]] = {}
        self._candado = threading.Lock()

    def obtener(self, clave: str) -> EvaluacionDeLista:
        ahora = time.time()
        with self._candado:
            for vencida in [k for k, (_, t) in self._listas.items() if ahora - t > DURACION_LISTA_SEGUNDOS]:
                del self._listas[vencida]
            evaluacion, _ = self._listas.get(clave, (None, 0))
            if evaluacion is None:
                evaluacion = EvaluacionDeLista()
                evaluacion.iniciarLista()
            self._listas[clave] = (evaluacion, ahora)
            return evaluacion


def crearAplicacion() -> Flask:
    app = Flask(__name__, template_folder=os.path.join(DIRECTORIO_PAGINAS, "templates"),
                static_folder=os.path.join(DIRECTORIO_PAGINAS, "static"))
    app.secret_key = os.environ.get("CLAVE_SESION") or secrets.token_hex(32)
    listas = ListasEnMemoria()

    def controladorDeLista() -> CtrlListaDeCompras:
        if "lista" not in session:
            session["lista"] = uuid.uuid4().hex
        return CtrlListaDeCompras(listas.obtener(session["lista"]))

    # --- CU-S01 Comparar precios de un producto ------------------------------
    @app.get("/")
    def comparacion():
        termino = request.args.get("termino")
        if termino is None:
            return CtrlComparacion().mostrar()
        return CtrlComparacion().buscar(termino, request.args.get("cadena"))

    # --- CU-S02 Evaluar lista de compras -------------------------------------
    @app.get("/lista")
    def lista():
        return controladorDeLista().mostrar()

    @app.post("/lista/agregar")
    def agregar_producto():
        return controladorDeLista().agregarProducto(request.form.get("nombre", ""), request.form.get("cantidad"))

    @app.post("/lista/quitar")
    def quitar_producto():
        return controladorDeLista().quitarProducto(request.form.get("nombre", ""))

    @app.post("/lista/evaluar")
    def evaluar_lista():
        return controladorDeLista().evaluarLista()

    @app.post("/lista/nueva")
    def nueva_lista():
        return controladorDeLista().iniciarLista()

    # --- CU-S03 Consultar historial de precios -------------------------------
    @app.get("/historial/<int:id_producto>")
    def historial(id_producto: int):
        return CtrlHistorial().consultarHistorial(
            id_producto, request.args.get("fecha_inicio"), request.args.get("fecha_fin"),
            request.args.get("producto", ""), request.args.get("cadena"),
            request.args.get("volver") or url_for("comparacion"))

    # --- CU-S04 Ubicar tiendas cercanas --------------------------------------
    @app.get("/tiendas")
    def tiendas():
        return CtrlTiendasCercanas().mostrar()

    @app.post("/tiendas")
    def tiendas_ubicar():
        return CtrlTiendasCercanas().mostrarTiendas(request.form.get("latitud"), request.form.get("longitud"))

    @app.post("/tiendas/datos")
    def tiendas_datos():
        # Usado por la lista de compras (CU-S02, extensión 5b) para mostrar la sucursal más cercana.
        tiendas = CtrlTiendasCercanas().ubicarTiendas(request.form.get("latitud"), request.form.get("longitud"))
        if tiendas is None:
            return jsonify({"error": "posición no válida"}), 400
        return jsonify(tiendas)

    @app.get("/inicio")
    def inicio():
        return redirect(url_for("comparacion"))

    return app
