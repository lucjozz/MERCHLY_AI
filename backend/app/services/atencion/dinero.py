"""Formato de montos y guardia "los números nunca salen del modelo" (docs/007-Agentes/09, secciones 1 y 8)."""

import re
from decimal import Decimal

from app.services.importar_inventario import parsear_numero

_MONTO = re.compile(
    r"(?:(?:bs\.?|bob|us\$|usd|\$)\s*([0-9][0-9.,]*))|(?:([0-9][0-9.,]*)\s*(?:bs\b|bs\.|bolivianos|bob\b|d[oó]lares|usd\b))",
    re.IGNORECASE,
)


def formatear(monto: Decimal | None, moneda: str) -> str:
    """Bs 450 · Bs 12,50 · US$ 9,90 (formato boliviano: punto de miles, coma decimal)."""
    if monto is None:
        return "precio a consultar"
    monto = Decimal(monto).quantize(Decimal("0.01"))
    entero, decimales = f"{monto:,.2f}".split(".")
    texto = entero.replace(",", ".") + ("" if decimales == "00" else f",{decimales}")
    return f"{'US$' if moneda == 'USD' else 'Bs'} {texto}"


def montos_en_texto(texto: str) -> list[Decimal]:
    """Todos los montos con moneda que aparecen en un texto."""
    encontrados = []
    for a, b in _MONTO.findall(texto or ""):
        valor = parsear_numero((a or b).rstrip(".,"))
        if valor is not None:
            encontrados.append(valor)
    return encontrados


def montos_no_permitidos(texto: str, permitidos: set[Decimal]) -> list[Decimal]:
    """Montos del texto que no salieron de la base (precio, envío, subtotal, total)."""
    permitidos_q = {Decimal(p).quantize(Decimal("0.01")) for p in permitidos}
    return [m for m in montos_en_texto(texto) if m not in permitidos_q]
