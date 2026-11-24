"""Proveedor SIMULADO del Agente de Atención (sin IA): reglas simples en español.

Sirve para probar todo el flujo sin claves de IA. Usa exactamente las mismas
herramientas (sub-agentes) que la IA real, y sus respuestas se marcan como
simuladas en la interfaz.
"""

import re

from app.services.atencion.herramientas import Herramientas
from app.services.atencion.stock import normalizar, palabras

NUMEROS = {"un": 1, "una": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "diez": 10}
QUIERE_HUMANO = re.compile(
    r"\b(descuento|rebaja|oferta especial|reclamo|devolucion|devolver|garantia|estafa|persona|humano|encargado|"
    r"dueno|hablar con|atencion humana|queja|mal servicio)\b"
)
PAGO = re.compile(r"\b(ya pague|pague|ya transferi|transferi|deposite|comprobante|ya esta pagado|listo el pago|hice el pago)\b")
COMPRA = re.compile(r"\b(lo quiero|la quiero|los quiero|quiero comprar|comprar|lo llevo|me lo llevo|me la llevo|confirmo|quiero \d+|quiero (un|una|dos|tres))\b")
ENVIO = re.compile(r"\b(envio|envios|delivery|enviar|envian|mandan|llega|domicilio|zona)\b")
CATALOGO = re.compile(r"\b(catalogo|que tenes|que tienen|que venden|que productos|lista de precios|productos)\b")
INFO = re.compile(r"\b(horario|horarios|atienden|abren|cierran|direccion|donde estan|ubicacion|local|formas de pago|aceptan|tarjeta)\b")
SALUDO = re.compile(r"^\s*(hola|buenas|buen dia|buenos dias|buenas tardes|buenas noches|que tal)\b[\s!.,]*$")


def _cantidad(texto: str) -> int:
    for palabra in normalizar(texto).split():
        if palabra.isdigit() and 0 < int(palabra) <= 100:
            return int(palabra)
        if palabra in NUMEROS:
            return NUMEROS[palabra]
    return 1


def _lista(productos: list[dict]) -> str:
    lineas = []
    for p in productos:
        disponible = f"{p['disponibles']} disponibles" if p["disponibles"] > 0 else "agotado"
        lineas.append(f"• {p['nombre']}: {p['precio']} ({disponible})")
    return "\n".join(lineas)


class ProveedorAtencionSimulado:
    nombre = "simulado"

    async def responder(
        self, texto: str, historial: list[tuple[str, str]], h: Herramientas, presentacion: str, info_negocio: str = ""
    ) -> str:
        normal = normalizar(texto)

        if QUIERE_HUMANO.search(normal):
            await h.ejecutar("derivar_a_persona", {"motivo": texto[:200]})
            return "Te paso con una persona del negocio para que lo vea con vos. En un ratito te escriben."

        if PAGO.search(normal):
            r = await h.ejecutar("informar_pago", {})
            if "error" in r:
                return "No encuentro un pedido pendiente de pago. ¿Querés que armemos uno?"
            return f"¡Gracias! Le avisé al vendedor que pagaste {r['total']}. Apenas lo vea en su cuenta te confirma."

        if INFO.search(normal):
            if info_negocio:
                return info_negocio[:800]
            await h.ejecutar("derivar_a_persona", {"motivo": texto[:200]})
            return "Esa info te la pasa el vendedor en un ratito."

        if SALUDO.match(normal):
            return f"{presentacion} ¿Qué estás buscando?"

        if COMPRA.search(normal):
            productos = h.ultimos_productos
            if not productos or palabras(re.sub(COMPRA, " ", normal)):
                r = await h.ejecutar("buscar_productos", {"consulta": texto})
                productos = h.ultimos_productos if r.get("productos") else productos
            if not productos:
                return "¿Cuál producto querés? Decime el nombre y te paso el precio."
            producto = productos[0]
            zona = None
            if ENVIO.search(normal) or " a " in f" {normal} ":
                cotizacion = await h.ejecutar("cotizar_envio", {"zona": texto})
                zona = cotizacion.get("zona")
            r = await h.ejecutar(
                "armar_pedido",
                {"items": [{"producto_id": str(producto.id), "cantidad": _cantidad(texto)}], "zona": zona,
                 "nombre_comprador": None, "direccion": None},
            )
            if "error" in r:
                return r["error"]
            detalle = "\n".join(f"• {linea}" for linea in r["pedido"])
            envio = f"Envío: {r['envio']}\n" if zona else "Envío: decime tu zona y te digo el costo.\n"
            if r["qr_enviado"]:
                return (
                    f"¡Perfecto! Tu pedido:\n{detalle}\n{envio}Total: {r['total']}\n\n"
                    f"Te mando el QR para pagar. Te lo reservo {r['reserva_minutos']} minutos. Cuando pagues, avisame."
                )
            return f"¡Genial! Tu pedido:\n{detalle}\n{envio}Total: {r['total']}\n\nLe paso tu pedido al vendedor y te escribe para cerrarlo."

        if ENVIO.search(normal):
            r = await h.ejecutar("cotizar_envio", {"zona": texto})
            if "zona" in r:
                return f"El envío a {r['zona']} cuesta aprox. {r['costo_estimado']}."
            if "zonas" in r:
                zonas = "\n".join(f"• {z['zona']}: {z['costo_estimado']}" for z in r["zonas"])
                return f"Hacemos envíos a estas zonas (costo estimado):\n{zonas}\n¿A cuál te lo mandamos?"
            return "Sí hacemos envíos: el vendedor te confirma el costo según tu zona."

        if CATALOGO.search(normal):
            r = await h.ejecutar("ver_catalogo", {})
            if not r["productos"]:
                return "Todavía no tenemos productos publicados. Te paso con el vendedor."
            return f"Esto es lo que tenemos:\n{_lista(r['productos'])}\n¿Te interesa alguno?"

        r = await h.ejecutar("buscar_productos", {"consulta": texto})
        if r.get("productos"):
            return f"Tengo esto:\n{_lista(r['productos'])}\n¿Lo querés?"
        if palabras(texto):
            return "No encontré eso en el catálogo. ¿Me lo describís de otra forma? Si querés, te paso con el vendedor."
        return f"{presentacion} ¿En qué te ayudo?"
