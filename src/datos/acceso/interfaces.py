"""Interfaces que ofrecen los componentes de acceso a datos (Figuras 12 y 15)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from src.negocio.entidades import (CadenaDeSupermercados, EtiquetaDeAnaquel, Producto,
                                   ResultadoDeRecoleccion, Tienda)


class IProductoDAC(ABC):
    @abstractmethod
    def buscar(self, termino: str, cadena: str | None) -> list[Producto]: ...

    @abstractmethod
    def buscarPorNombre(self, nombre: str) -> Producto | None: ...

    @abstractmethod
    def obtenerConHistorial(self, idProducto: int, fechaInicio: date, fechaFin: date) -> Producto | None: ...

    @abstractmethod
    def obtenerOCrear(self, datos) -> Producto: ...


class ICadenaDAC(ABC):
    @abstractmethod
    def obtenerCadenas(self) -> list[CadenaDeSupermercados]: ...

    @abstractmethod
    def obtenerTiendas(self) -> list[Tienda]: ...


class IEtiquetaDAC(ABC):
    @abstractmethod
    def guardar(self, etiquetas: list[EtiquetaDeAnaquel]) -> None: ...


class IRecoleccionDAC(ABC):
    @abstractmethod
    def guardarResultado(self, resultado: ResultadoDeRecoleccion) -> None: ...
