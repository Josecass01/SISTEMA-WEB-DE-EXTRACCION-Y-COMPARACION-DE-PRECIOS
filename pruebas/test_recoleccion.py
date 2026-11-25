"""Pruebas del flujo de recolección (CU-S05) con agentes simulados."""
import sqlite3

from src import configuracion
from src.datos.agentes.agente_ara import AgenteAra
from src.datos.agentes.agente_de_supermercado import (AgenteDeSupermercado, FuenteNoDisponible,
                                                      ProductoPublicado)
from src.datos.agentes.conversion import extraerContenido, limpiarPrecio
from src.negocio.flujo.recoleccion_de_precios import RecoleccionDePrecios


class AgenteFijo(AgenteDeSupermercado):
    def __init__(self, cadena, productos=None, fallar=False):
        self._cadena, self._productos, self._fallar = cadena, productos or [], fallar

    @property
    def cadena(self):
        return self._cadena

    def obtenerProductos(self):
        if self._fallar:
            raise FuenteNoDisponible("sin respuesta")
        return self._productos


def _consultar(sql):
    with sqlite3.connect(configuracion.RUTA_BASE_DE_DATOS) as c:
        return c.execute(sql).fetchall()


def test_recoleccion_guarda_precios_y_registra_resultados():
    publicados = [
        ProductoPublicado("Panela Prueba 500g", 500, "g", 2500, None),
        ProductoPublicado("", 500, "g", 2500, None),             # extensión 2c: sin nombre
        ProductoPublicado("Sal Prueba 1kg", 1000, "g", 0, None),  # extensión 2c: sin precio
    ]
    agentes = [AgenteFijo("D1", publicados), AgenteFijo("Olímpica", fallar=True)]
    RecoleccionDePrecios(agentes=agentes, esperaReintento=0).ejecutar()

    assert _consultar("SELECT COUNT(*) FROM producto WHERE descripcion = 'Panela Prueba 500g'") == [(1,)]
    estados = dict(_consultar(
        "SELECT c.nombre, r.estado FROM resultado_recoleccion r "
        "JOIN cadena_supermercado c ON c.id_cadena = r.id_cadena"))
    assert estados["D1"] == "finalizada"
    assert estados["Olímpica"] == "pausada"


def test_agente_ara_simulado_es_estable_en_el_dia():
    from datetime import date
    primero = AgenteAra(fecha=date(2026, 11, 24)).obtenerProductos()
    segundo = AgenteAra(fecha=date(2026, 11, 24)).obtenerProductos()
    assert primero and [p.precio for p in primero] == [p.precio for p in segundo]
    assert all(p.precio % 10 == 0 for p in primero)


def test_conversion_de_textos_publicados():
    assert limpiarPrecio("$ 4.350") == 4350
    assert extraerContenido("Leche Entera 1.000Ml") == (1000, "ml")
    assert extraerContenido("Arroz x 5 kg") == (5000, "g")
