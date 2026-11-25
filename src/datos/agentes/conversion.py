"""Funciones de apoyo de los agentes para depurar textos y valores numéricos (RF-01)."""

from __future__ import annotations

import re


def limpiarPrecio(texto: str | float | int | None) -> int | None:
    """Convierte un precio publicado ('$12.900', '12.900,00', 12900.0) a pesos enteros."""
    if texto is None:
        return None
    if isinstance(texto, (int, float)):
        valor = int(round(texto))
        return valor if valor > 0 else None
    t = re.sub(r"[^\d.,]", "", texto.strip())
    if not t:
        return None
    if "." in t and "," in t:
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").split(",")[0]
        else:
            t = t.replace(",", "").split(".")[0]
    elif "." in t:
        partes = t.split(".")
        t = t.replace(".", "") if len(partes[-1]) == 3 else partes[0]
    elif "," in t:
        partes = t.split(",")
        t = t.replace(",", "") if len(partes[-1]) == 3 else partes[0]
    return int(t) if t.isdigit() and int(t) > 0 else None


def extraerContenido(nombre: str) -> tuple[float, str] | None:
    """
    Obtiene el contenido neto y su unidad a partir del nombre publicado.

    Devuelve (cantidad, unidad) con unidad 'g', 'ml' o 'u', o None si el
    nombre no indica el contenido (en ese caso el registro no se almacena,
    CU-S05, extensión 2c).
    """
    n = nombre.lower()
    n = re.sub(r"(\d)\.(\d{3})(?!\d)", r"\1\2", n)  # separador de miles: 1.000 ml
    n = n.replace(",", ".")
    patrones = [
        (r"(\d+(?:\.\d+)?)\s*(?:kg|kilo(?:gramo)?s?)\b", "g", 1000),
        (r"(\d+(?:\.\d+)?)\s*(?:g|gr|grs|gramos?)\b", "g", 1),
        (r"(\d+(?:\.\d+)?)\s*(?:ml|mililitros?|cc)\b", "ml", 1),
        (r"(\d+(?:\.\d+)?)\s*(?:l|lt|lts|litros?)\b", "ml", 1000),
        (r"(?:x|×)\s*(\d+)\s*(?:und|unds|unidades|u)?\b", "u", 1),
        (r"(\d+)\s*(?:und|unds|unidades|rollos|huevos)\b", "u", 1),
    ]
    for patron, unidad, factor in patrones:
        m = re.search(patron, n)
        if m:
            cantidad = float(m.group(1)) * factor
            if cantidad > 0:
                return cantidad, unidad
    return None


def limpiarNombre(nombre: str) -> str:
    """Normaliza espacios y mayúsculas del nombre publicado."""
    n = re.sub(r"\s+", " ", nombre).strip()
    if n and n == n.upper():
        n = n.title()
    return n
