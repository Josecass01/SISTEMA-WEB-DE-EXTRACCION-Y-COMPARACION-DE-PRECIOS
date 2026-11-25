"""Controlador del caso de uso CU-S03 Consultar historial de precios (Figuras 14 y 19)."""

from __future__ import annotations

from collections import OrderedDict
from datetime import date, datetime

from src import configuracion
from src.negocio.componentes import HistorialDePrecios, IHistorial
from src.presentacion.paginas import PaginaHistorial

CADENAS = ["Ara", "D1", "Olímpica"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def leerFecha(texto: str) -> date | None:
    try:
        return datetime.strptime((texto or "").strip(), "%d/%m/%Y").date()
    except ValueError:
        return None


def restarMeses(fecha: date, meses: int) -> date:
    mes = fecha.month - meses
    anio = fecha.year + (mes - 1) // 12
    mes = (mes - 1) % 12 + 1
    return date(anio, mes, min(fecha.day, 28))


class CtrlHistorial:
    def __init__(self, historial: IHistorial | None = None, pagina: PaginaHistorial | None = None):
        self._historial = historial or HistorialDePrecios()
        self._pagina = pagina or PaginaHistorial()

    def consultarHistorial(self, idProducto: int, fechaInicio: str | None, fechaFin: str | None,
                           producto: str, cadena: str | None, volver: str) -> str:
        cadena = cadena if cadena in CADENAS else None
        datos = {"id_producto": idProducto, "producto": producto, "cadena": cadena,
                 "cadenas": CADENAS, "volver": volver}

        if not fechaInicio and not fechaFin:
            # Intervalo inicial: los últimos 12 meses (Tabla 18).
            fin = date.today()
            inicio = restarMeses(fin, configuracion.INTERVALO_MAXIMO_HISTORIAL_MESES)
        else:
            inicio, fin = leerFecha(fechaInicio), leerFecha(fechaFin)
            if inicio is None or fin is None:
                return self._pagina.mostrar(mensaje="Escriba las fechas con el formato dd/mm/aaaa.",
                                            error=True, fecha_inicio=fechaInicio, fecha_fin=fechaFin, **datos)
        datos.update(fecha_inicio=inicio.strftime("%d/%m/%Y"), fecha_fin=fin.strftime("%d/%m/%Y"))

        if inicio > fin:  # CU-S03, extensión 2a
            return self._pagina.mostrar(
                mensaje="La fecha inicial es posterior a la fecha final. Corrija el intervalo de fechas.",
                error=True, **datos)
        if inicio < restarMeses(fin, configuracion.INTERVALO_MAXIMO_HISTORIAL_MESES):
            return self._pagina.mostrar(
                mensaje=f"El intervalo no puede superar {configuracion.INTERVALO_MAXIMO_HISTORIAL_MESES} meses. "
                        "Corrija el intervalo de fechas.", error=True, **datos)

        etiquetas = self._historial.consultar(idProducto, inicio, fin)
        if cadena:  # CU-S03, extensión 3b
            etiquetas = [e for e in etiquetas if e.cadena.nombre == cadena]
        if not etiquetas:  # CU-S03, extensión 3a
            return self._pagina.mostrar(mensaje="No hay registros de precios para el periodo seleccionado.",
                                        **datos)

        series: dict[str, list[dict]] = {}
        for e in etiquetas:
            series.setdefault(e.cadena.nombre, []).append({"fecha": e.fecha.isoformat(), "precio": e.precio})
        return self._pagina.mostrar(series=series, tabla=self._tablaPorMes(etiquetas),
                                    cadenas_con_datos=[c for c in CADENAS if c in series],
                                    fechaRecoleccion=etiquetas[-1].fecha, **datos)

    @staticmethod
    def _tablaPorMes(etiquetas) -> list[dict]:
        """Último precio registrado de cada cadena en cada mes (alternativa a la gráfica)."""
        meses: OrderedDict[tuple[int, int], dict] = OrderedDict()
        for e in sorted(etiquetas, key=lambda x: x.fecha):
            clave = (e.fecha.year, e.fecha.month)
            fila = meses.setdefault(clave, {"mes": f"{MESES[e.fecha.month - 1].capitalize()} de {e.fecha.year}"})
            fila[e.cadena.nombre] = e.precio
        return list(meses.values())
