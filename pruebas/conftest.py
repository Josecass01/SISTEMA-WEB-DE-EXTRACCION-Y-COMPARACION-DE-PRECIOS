"""Cada prueba trabaja sobre una copia de la base de datos inicial."""
import shutil

import pytest

from src import configuracion


@pytest.fixture(autouse=True)
def base_de_datos(tmp_path, monkeypatch):
    ruta = tmp_path / "paracompara.db"
    shutil.copyfile(configuracion.RUTA_BASE_DE_DATOS_INICIAL, ruta)
    monkeypatch.setattr(configuracion, "RUTA_BASE_DE_DATOS", ruta)
    return ruta


@pytest.fixture
def cliente():
    from src.presentacion.aplicacion import crearAplicacion
    app = crearAplicacion()
    app.config["TESTING"] = True
    return app.test_client()
