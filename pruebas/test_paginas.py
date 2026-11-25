"""Pruebas de las pantallas a través de los controladores (Figuras 9 a 11)."""


def test_comparar_precios(cliente):
    respuesta = cliente.get("/?termino=arroz")
    texto = respuesta.get_data(as_text=True)
    assert respuesta.status_code == 200
    assert "ordenados del menor al mayor precio por unidad de medida" in texto
    assert "Menor PUM" in texto


def test_comparar_precios_rechaza_texto_sin_letras(cliente):
    texto = cliente.get("/?termino=1234").get_data(as_text=True)
    assert 'class="mensaje error"' in texto


def test_lista_de_compras(cliente):
    cliente.get("/lista")
    cliente.post("/lista/agregar", data={"nombre": "arroz blanco 500g", "cantidad": "2"})
    cliente.post("/lista/agregar", data={"nombre": "leche entera 1l", "cantidad": "1"})
    texto = cliente.post("/lista/evaluar").get_data(as_text=True)
    assert "Costo total de la lista por supermercado" in texto
    assert "Opción más económica" in texto


def test_tiendas_cercanas(cliente):
    respuesta = cliente.post("/tiendas/datos", data={"latitud": "10.39", "longitud": "-75.48"})
    tiendas = respuesta.get_json()
    assert tiendas and all(t["distancia_km"] <= 10 for t in tiendas)
    assert [t["distancia_km"] for t in tiendas] == sorted(t["distancia_km"] for t in tiendas)


def test_historial_rechaza_intervalo_mayor_a_12_meses(cliente):
    texto = cliente.get("/historial/338?fecha_inicio=01/01/2025&fecha_fin=01/06/2026").get_data(as_text=True)
    assert 'class="mensaje error"' in texto


def test_historial_rechaza_fecha_inicial_posterior(cliente):
    texto = cliente.get("/historial/338?fecha_inicio=01/06/2026&fecha_fin=01/01/2026").get_data(as_text=True)
    assert 'class="mensaje error"' in texto
