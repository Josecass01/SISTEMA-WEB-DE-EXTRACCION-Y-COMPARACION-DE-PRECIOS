"""Controlador del caso de uso CU-S04 Ubicar tiendas cercanas (Figuras 14 y 20)."""

from __future__ import annotations

from src import configuracion
from src.negocio.componentes import IUbicacion, UbicacionDeTiendas
from src.presentacion.paginas import PaginaTiendasCercanas


class CtrlTiendasCercanas:
    def __init__(self, ubicacion: IUbicacion | None = None, pagina: PaginaTiendasCercanas | None = None):
        self._ubicacion = ubicacion or UbicacionDeTiendas()
        self._pagina = pagina or PaginaTiendasCercanas()

    def mostrar(self) -> str:
        return self._pagina.mostrar(radio=configuracion.RADIO_DE_COBERTURA_KM)

    def ubicarTiendas(self, latitud, longitud) -> list[dict] | None:
        """
        Sucursales ordenadas de la más cercana a la más lejana, o None si la
        posición no es válida (CU-S04, extensión 3b). La posición no se almacena.
        """
        posicion = self._validar(latitud, longitud)
        if posicion is None:
            return None
        return [{"cadena": t.cadena.nombre if t.cadena else "", "nombre": t.nombre,
                 "direccion": t.direccion, "distancia_km": round(d, 2)}
                for t, d in self._ubicacion.ubicar(*posicion)]

    def mostrarTiendas(self, latitud, longitud) -> str:
        tiendas = self.ubicarTiendas(latitud, longitud)
        if tiendas is None:
            return self._pagina.mostrar(
                radio=configuracion.RADIO_DE_COBERTURA_KM, error=True,
                mensaje="No fue posible obtener una posición válida. Puede continuar sin información de distancia.")
        if not tiendas:
            return self._pagina.mostrar(
                radio=configuracion.RADIO_DE_COBERTURA_KM, tiendas=[],
                mensaje=f"No hay sucursales registradas a menos de {configuracion.RADIO_DE_COBERTURA_KM} km "
                        "de su ubicación.")
        mas_cercana = {}
        for t in tiendas:
            mas_cercana.setdefault(t["cadena"], t)
        return self._pagina.mostrar(
            radio=configuracion.RADIO_DE_COBERTURA_KM, tiendas=tiendas, mas_cercana=mas_cercana,
            mensaje=f"{len(tiendas)} sucursales a menos de {configuracion.RADIO_DE_COBERTURA_KM} km, "
                    "ordenadas de la más cercana a la más lejana. Su ubicación no se guarda.")

    @staticmethod
    def _validar(latitud, longitud) -> tuple[float, float] | None:
        try:
            lat, lon = float(latitud), float(longitud)
        except (TypeError, ValueError):
            return None
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None
        return lat, lon
