"""Entidad de negocio Comprador (Figura 13)."""

from .lista_de_compras import ListaDeCompras


class Comprador:
    """Persona que consulta el sistema. No se almacena: no hay cuentas de usuario."""

    def crearListaDeCompras(self) -> ListaDeCompras:
        """Crea una lista de compras vacía (patrón Creador)."""
        return ListaDeCompras()
