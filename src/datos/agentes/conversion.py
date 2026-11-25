"""Conversión de los textos publicados por las cadenas (precio y contenido neto)."""

from __future__ import annotations

import re

# Unidad publicada -> (unidad del sistema, factor).
_UNIDADES = {
    "kg": ("g", 1000), "kgs": ("g", 1000), "kilo": ("g", 1000), "kilos": ("g", 1000),
    "kilogramo": ("g", 1000), "kilogramos": ("g", 1000),
    "g": ("g", 1), "gr": ("g", 1), "grs": ("g", 1), "gramo": ("g", 1), "gramos": ("g", 1),
    "mg": ("g", 0.001),
    "l": ("ml", 1000), "lt": ("ml", 1000), "lts": ("ml", 1000), "litro": ("ml", 1000), "litros": ("ml", 1000),
    "ml": ("ml", 1), "cc": ("ml", 1), "cm3": ("ml", 1),
    "und": ("u", 1), "unds": ("u", 1), "un": ("u", 1), "unid": ("u", 1), "unidad": ("u", 1),
    "unidades": ("u", 1), "u": ("u", 1),
}

_PATRON_CONTENIDO = re.compile(
    r"(?<![\w.,])(\d+(?:[.,]\d+)*)\s*(" + "|".join(sorted(_UNIDADES, key=len, reverse=True)) + r")(?![a-z])",
    re.IGNORECASE)


def _numero(texto: str) -> float:
    """Interpreta '1.000' y '1,000' como mil, y '1.5' o '1,5' como decimales."""
    texto = texto.strip()
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", texto):
        return float(re.sub(r"[.,]", "", texto))
    return float(texto.replace(",", "."))


def _entero_si_es_posible(valor: float) -> float | int:
    return int(valor) if float(valor).is_integer() else round(valor, 3)


def limpiarPrecio(texto: str | float | int | None) -> float:
    """'$ 4.350' -> 4350. Devuelve 0 si el texto no contiene un precio."""
    if texto is None:
        return 0
    if isinstance(texto, (int, float)):
        return _entero_si_es_posible(float(texto))
    digitos = re.sub(r"[^\d.,]", "", str(texto))
    if not digitos:
        return 0
    # En Colombia el punto separa miles; los centavos casi nunca se publican.
    if re.fullmatch(r"\d+[.,]\d{1,2}", digitos):
        return _entero_si_es_posible(float(digitos.replace(",", ".")))
    return _entero_si_es_posible(float(re.sub(r"[.,]", "", digitos)))


def extraerContenido(nombre: str) -> tuple[float, str] | None:
    """
    Contenido neto del producto a partir de su nombre, en la unidad base del
    sistema (g, ml o u). 'Leche Entera 1.000Ml' -> (1000, 'ml'); 'Arroz x 5 kg' -> (5000, 'g').
    """
    coincidencias = list(_PATRON_CONTENIDO.finditer(nombre or ""))
    if not coincidencias:
        return None
    # Si hay varias (p. ej. '6 und x 200 ml'), se toma la que no es de unidades.
    elegida = next((c for c in reversed(coincidencias) if _UNIDADES[c.group(2).lower()][0] != "u"),
                   coincidencias[-1])
    unidad, factor = _UNIDADES[elegida.group(2).lower()]
    cantidad = _numero(elegida.group(1)) * factor
    if cantidad <= 0:
        return None
    return _entero_si_es_posible(cantidad), unidad
