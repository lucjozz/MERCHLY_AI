"""Guardia de salida del Agente de Atención (docs/007-Agentes/09, secciones 4 y 8).

Última barrera antes de mandarle algo a un comprador. Aunque la IA sea
engañada ("ignorá tus reglas"), la respuesta no sale si:
* menciona un monto que no salió de los sub-agentes;
* promete descuentos, regalos o envíos gratis;
* dice que un pago está confirmado (eso lo hace solo una persona);
* habla de costos internos, ganancia o margen.
"""

import re
import unicodedata
from decimal import Decimal

from app.services.atencion.dinero import montos_no_permitidos


def _normal(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()


PROMESAS = re.compile(
    r"(te (hago|dejo|doy|aplico|regalo)\b.{0,25}\b(descuento|rebaja|precio especial|gratis|de regalo))"
    r"|(\b\d{1,2} ?% ?(de )?(descuento|off|menos)\b)"
    r"|(\b(envio|delivery) (es |sale |va )?(gratis|sin costo|bonificado)\b)"
    r"|(\b(2x1|3x2|dos por uno)\b)"
    r"|(\bte lo (dejo|doy) (a|en) (mitad de precio|precio de costo)\b)"
)
PAGO_CONFIRMADO = re.compile(
    r"\b(pago (esta |quedo |fue )?(confirmado|aprobado|acreditado|verificado)"
    r"|(confirme|verifique|recibi|vi) (tu|el|su) (pago|deposito|transferencia)"
    r"|ya (esta|quedo) pagado|(tu|el) pedido (esta|quedo) pagado)\b"
)
INTERNOS = re.compile(r"\b(nos costo|me costo|costo unitario|precio de costo|costo interno|nuestro costo|ganancia|margen de|lo compramos a|proveedor)\b")


def revisar(texto: str, montos_permitidos: set[Decimal]) -> str | None:
    """None si la respuesta se puede mandar; si no, el motivo (para el aviso al dueño)."""
    if montos_no_permitidos(texto, montos_permitidos):
        return "mencionó un precio que no está en tu catálogo"
    normal = _normal(texto)
    if PROMESAS.search(normal):
        return "prometió un descuento o algo gratis"
    if PAGO_CONFIRMADO.search(normal):
        return "dijo que un pago estaba confirmado"
    if INTERNOS.search(normal):
        return "habló de costos internos"
    return None
