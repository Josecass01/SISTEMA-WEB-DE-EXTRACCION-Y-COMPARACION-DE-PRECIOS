"""Interfaces que ofrecen los componentes de negocio a los controladores (Figuras 12 y 14)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from src.negocio.entidades import EtiquetaDeAnaquel


class IComparacion(ABC):
    @abstractmethod
    def compararPrecios(self, termino: str, cadena: str | None) -> list[EtiquetaDeAnaquel]: ...


class IListaDeCompras(ABC):
    @abstractmethod
    def iniciarLista(self) -> None: ...

    @abstractmethod
    def agregarProducto(self, nombre: str, cantidad: int): ...

    @abstractmethod
    def quitarProducto(self, nombre: str) -> None: ...

    @abstractmethod
    def evaluarLista(self): ...


class IHistorial(ABC):
    @abstractmethod
    def consultar(self, idProducto: int, fechaInicio: date, fechaFin: date) -> list[EtiquetaDeAnaquel]: ...


class IUbicacion(ABC):
    @abstractmethod
    def ubicar(self, latitud: float, longitud: float): ...
