"""Interfaces de los componentes de acceso a datos (DAC) que usa la capa de negocio."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import TYPE_CHECKING

from src.negocio.entidades import (CadenaDeSupermercados, EtiquetaDeAnaquel, Producto,
                                   ResultadoDeRecoleccion, Tienda)

if TYPE_CHECKING:
    from src.datos.agentes.agente_de_supermercado import ProductoPublicado


class IProductoDAC(ABC):
    @abstractmethod
    def buscar(self, termino: str, cadena: str | None = None) -> list[Producto]: ...

    @abstractmethod
    def buscarPorNombre(self, nombre: str) -> Producto | None: ...

    @abstractmethod
    def obtenerConHistorial(self, idProducto: int, fechaInicio: date, fechaFin: date) -> Producto | None: ...

    @abstractmethod
    def obtenerOCrear(self, datos: ProductoPublicado) -> Producto: ...


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
