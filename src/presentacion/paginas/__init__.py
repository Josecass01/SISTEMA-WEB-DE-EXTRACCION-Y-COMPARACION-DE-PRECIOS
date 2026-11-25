"""
Páginas de la interfaz de usuario («GUI», sección 3.1.2 del Manual del sistema).

Cada página solo presenta los datos que recibe de su controlador; no contiene
lógica de negocio.
"""

from __future__ import annotations

from datetime import date

from flask import render_template

NOMBRES_UNIDAD = {"g": "gramo", "kg": "gramo", "ml": "mililitro", "l": "mililitro", "u": "unidad"}


def formatoPesos(valor: float | None) -> str:
    if valor is None:
        return ""
    return "$ " + f"{int(round(valor)):,}".replace(",", ".")


def formatoPUM(etiqueta) -> str:
    unidad = NOMBRES_UNIDAD.get(etiqueta.producto.unidadDeMedida, "unidad")
    valor = f"{etiqueta.pum:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"$ {valor} por {unidad}"


def formatoFecha(valor: date | None) -> str:
    return valor.strftime("%d/%m/%Y") if valor else ""


class Pagina:
    plantilla = ""
    opcionDelMenu = ""

    def mostrar(self, fechaRecoleccion: date | None = None, **datos) -> str:
        """Genera la página con los datos que entrega el controlador."""
        return render_template(
            self.plantilla,
            opcion_activa=self.opcionDelMenu,
            fecha_recoleccion=formatoFecha(fechaRecoleccion),
            pesos=formatoPesos, pum=formatoPUM, fecha=formatoFecha,
            **datos,
        )


class PaginaComparacion(Pagina):
    plantilla = "comparacion.html"
    opcionDelMenu = "comparar"


class PaginaListaDeCompras(Pagina):
    plantilla = "lista_de_compras.html"
    opcionDelMenu = "lista"


class PaginaHistorial(Pagina):
    plantilla = "historial.html"
    opcionDelMenu = "comparar"


class PaginaTiendasCercanas(Pagina):
    plantilla = "tiendas_cercanas.html"
    opcionDelMenu = "tiendas"
