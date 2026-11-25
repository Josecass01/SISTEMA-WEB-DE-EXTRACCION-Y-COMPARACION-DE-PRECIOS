"""Pruebas de las clases de la capa de negocio (Figura 13)."""
from datetime import date

from src.negocio.entidades import (CadenaDeSupermercados, ListaDeCompras, Producto, Tienda)

HOY = date(2026, 11, 24)


def test_pum_por_gramo():
    arroz = Producto("Arroz 500g", "Granos", 500, "g")
    d1 = CadenaDeSupermercados("D1")
    etiqueta = d1.registrarPrecio(arroz, 1850, None, HOY)
    assert etiqueta.pum == 3.7


def test_pum_convierte_kilogramos_a_gramos():
    arroz = Producto("Arroz 5kg", "Granos", 5, "kg")
    etiqueta = CadenaDeSupermercados("D1").registrarPrecio(arroz, 6500, None, HOY)
    assert etiqueta.pum == 1.3


def test_precios_ordenados_por_pum():
    producto = Producto("Leche 1L", "Lácteos", 1000, "ml")
    for nombre, precio in [("Ara", 4300), ("D1", 3900), ("Olímpica", 4100)]:
        CadenaDeSupermercados(nombre).registrarPrecio(producto, precio, None, HOY)
    assert [e.cadena.nombre for e in producto.obtenerPreciosOrdenadosPorPUM()] == ["D1", "Olímpica", "Ara"]


def test_costo_total_y_productos_no_incluidos():
    ara, d1 = CadenaDeSupermercados("Ara"), CadenaDeSupermercados("D1")
    arroz = Producto("Arroz 500g", "Granos", 500, "g")
    aceite = Producto("Aceite 1L", "Aceites", 1000, "ml")
    ara.registrarPrecio(arroz, 1500, None, HOY)
    d1.registrarPrecio(arroz, 1800, None, HOY)
    d1.registrarPrecio(aceite, 9000, None, HOY)
    lista = ListaDeCompras()
    lista.agregarItem(arroz, 2)
    lista.agregarItem(aceite, 1)
    total_d1, faltantes_d1 = lista.calcularCostoTotal(d1)
    total_ara, faltantes_ara = lista.calcularCostoTotal(ara)
    assert (total_d1, faltantes_d1) == (12600, [])
    assert total_ara == 3000
    assert [i.producto.descripcion for i in faltantes_ara] == ["Aceite 1L"]


def test_agregar_el_mismo_producto_suma_cantidades():
    arroz = Producto("Arroz 500g", "Granos", 500, "g")
    lista = ListaDeCompras()
    lista.agregarItem(arroz, 1)
    lista.agregarItem(arroz, 2)
    assert len(lista.items) == 1 and lista.items[0].cantidad == 3


def test_distancia_entre_dos_puntos_de_cartagena():
    # Del Centro Histórico (Torre del Reloj) a Bocagrande hay unos 2,5 km en línea recta.
    tienda = Tienda("Prueba", "Bocagrande", 10.3997, -75.5543)
    assert 2.0 < tienda.calcularDistancia(10.4225, -75.5486) < 3.0
