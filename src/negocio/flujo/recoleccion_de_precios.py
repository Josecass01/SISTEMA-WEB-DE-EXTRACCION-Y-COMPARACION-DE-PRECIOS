"""Flujo de negocio RecoleccionDePrecios (Figura 14, CU-S05, Figura 21)."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from datetime import date

from src.datos.acceso import (CadenaDAC, EtiquetaDAC, ICadenaDAC, IEtiquetaDAC, IProductoDAC,
                              IRecoleccionDAC, ProductoDAC, RecoleccionDAC)
from src.datos.agentes import (AgenteAra, AgenteD1, AgenteDeSupermercado, AgenteOlimpica,
                               FormatoNoReconocido, FuenteNoDisponible)
from src.negocio.entidades import CadenaDeSupermercados, ResultadoDeRecoleccion

registro = logging.getLogger(__name__)

ESPERA_REINTENTO_SEGUNDOS = 300  # CU-S05, extensión 2a


class IRecoleccion(ABC):
    @abstractmethod
    def ejecutar(self) -> None: ...


class RecoleccionDePrecios(IRecoleccion):
    def __init__(self, agentes: list[AgenteDeSupermercado] | None = None,
                 cadenaDAC: ICadenaDAC | None = None, productoDAC: IProductoDAC | None = None,
                 etiquetaDAC: IEtiquetaDAC | None = None, recoleccionDAC: IRecoleccionDAC | None = None,
                 esperaReintento: float = ESPERA_REINTENTO_SEGUNDOS):
        # Agregar una cadena consiste en agregar su agente (principio abierto/cerrado).
        self._agentes = agentes if agentes is not None else [AgenteAra(), AgenteD1(), AgenteOlimpica()]
        self._cadenaDAC = cadenaDAC or CadenaDAC()
        self._productoDAC = productoDAC or ProductoDAC()
        self._etiquetaDAC = etiquetaDAC or EtiquetaDAC()
        self._recoleccionDAC = recoleccionDAC or RecoleccionDAC()
        self._esperaReintento = esperaReintento

    def ejecutar(self) -> None:
        for cadena in self._cadenaDAC.obtenerCadenas():
            self._recolectarCadena(cadena)

    def _recolectarCadena(self, cadena: CadenaDeSupermercados) -> None:
        agente = next((a for a in self._agentes if a.cadena == cadena.nombre), None)
        if agente is None:
            return
        hoy = date.today()
        try:
            publicados = self._obtenerConReintento(agente)
        except (FuenteNoDisponible, FormatoNoReconocido) as exc:
            # CU-S05, extensiones 2a y 2b: se registra el fallo y se continúa con las demás cadenas.
            registro.error("Recolección de %s pausada: %s", cadena.nombre, exc)
            self._recoleccionDAC.guardarResultado(
                ResultadoDeRecoleccion(cadena, hoy, ResultadoDeRecoleccion.PAUSADA, 0))
            return

        etiquetas = []
        for datos in publicados:
            # CU-S05, extensión 2c: no se almacenan registros sin nombre, sin contenido o sin precio.
            if not datos.nombre or datos.contenidoNeto <= 0 or datos.precio <= 0:
                continue
            producto = self._productoDAC.obtenerOCrear(datos)
            # La cadena crea la etiqueta (Creador) y la etiqueta calcula su PUM (Experto).
            etiquetas.append(cadena.registrarPrecio(producto, datos.precio, datos.precioPromocional, hoy))

        self._etiquetaDAC.guardar(etiquetas)  # una sola transacción por cadena
        self._recoleccionDAC.guardarResultado(
            ResultadoDeRecoleccion(cadena, hoy, ResultadoDeRecoleccion.FINALIZADA, len(etiquetas)))
        registro.info("Recolección de %s finalizada: %d precios", cadena.nombre, len(etiquetas))

    def _obtenerConReintento(self, agente: AgenteDeSupermercado):
        try:
            return agente.obtenerProductos()
        except FuenteNoDisponible:
            registro.warning("%s no respondió; se reintenta en %s s", agente.cadena, self._esperaReintento)
            time.sleep(self._esperaReintento)
            return agente.obtenerProductos()
