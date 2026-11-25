"""ProgramadorDeTareas (Figura 14): ejecuta la recolección a la hora definida en el sistema."""

from __future__ import annotations

import logging
import time

import schedule

from src import configuracion

from .recoleccion_de_precios import IRecoleccion, RecoleccionDePrecios

registro = logging.getLogger(__name__)


class ProgramadorDeTareas:
    def __init__(self, recoleccion: IRecoleccion | None = None,
                 horaProgramada: str = configuracion.HORA_RECOLECCION):
        self._recoleccion = recoleccion or RecoleccionDePrecios()
        self._horaProgramada = horaProgramada

    def iniciar(self) -> None:
        schedule.every().day.at(self._horaProgramada).do(self._recoleccion.ejecutar)
        registro.info("Recolección programada todos los días a las %s", self._horaProgramada)
        self._esperarHoraProgramada()

    def _esperarHoraProgramada(self) -> None:
        while True:
            schedule.run_pending()
            time.sleep(30)
