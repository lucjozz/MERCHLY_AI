"""Herramientas del orquestador: cada una es un sub-agente (docs/007-Agentes/09, sección 1).

La IA (real o simulada) elige cuáles llamar; acá se ejecutan con código
determinístico. Cada resultado trae los montos ya formateados y se anotan en
``montos_permitidos``: la respuesta final solo puede mencionar esos montos.
"""

import uuid
from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.atencion import Conversacion
from app.schemas.inventario import ItemCatalogoPublico
from app.services.atencion import envios, stock, venta
from app.services.atencion.conversaciones import derivar_a_persona
from app.services.atencion.dinero import formatear
from app.services.proveedores.seguridad_llm import limpiar_dato

# Definiciones para la IA real (function calling). Descripciones = contrato de cada sub-agente.
DEFINICIONES = [
    {
        "type": "function",
        "name": "buscar_productos",
        "description": "Sub-agente Catálogo/Stock: busca en el catálogo del negocio por nombre o características. Devuelve precio y cuántos hay disponibles.",
        "parameters": {
            "type": "object",
            "properties": {"consulta": {"type": "string", "description": "Lo que busca el comprador, ej. 'taladro 800W'"}},
            "required": ["consulta"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "ver_catalogo",
        "description": "Sub-agente Catálogo/Stock: lista los productos del catálogo (hasta 10) cuando el comprador pregunta qué venden.",
        "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "cotizar_envio",
        "description": "Sub-agente Envíos: costo estimado del envío a una zona. Sin zona, devuelve las zonas disponibles.",
        "parameters": {
            "type": "object",
            "properties": {"zona": {"type": ["string", "null"], "description": "Zona o barrio que dijo el comprador"}},
            "required": ["zona"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "armar_pedido",
        "description": "Sub-agente Venta: arma el pedido cuando el comprador CONFIRMA que quiere comprar. Calcula el total con los precios del catálogo.",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"producto_id": {"type": "string"}, "cantidad": {"type": "integer"}},
                        "required": ["producto_id", "cantidad"],
                        "additionalProperties": False,
                    },
                },
                "zona": {"type": ["string", "null"]},
                "nombre_comprador": {"type": ["string", "null"]},
                "direccion": {"type": ["string", "null"]},
            },
            "required": ["items", "zona", "nombre_comprador", "direccion"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "informar_pago",
        "description": "Sub-agente Venta: el comprador dice que ya pagó o mandó el comprobante. Avisa al vendedor para que lo confirme. NUNCA confirma el pago.",
        "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "derivar_a_persona",
        "description": "Pasa la conversación a una persona del negocio: descuentos, reclamos, devoluciones, enojo, algo que no sabés o si el comprador pide hablar con alguien.",
        "parameters": {
            "type": "object",
            "properties": {"motivo": {"type": "string"}},
            "required": ["motivo"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]
NOMBRES = {d["name"] for d in DEFINICIONES}


@dataclass
class Herramientas:
    db_session: AsyncSession
    conversacion: Conversacion
    moneda: str
    simulado: bool
    montos_permitidos: set[Decimal] = field(default_factory=set)
    adjuntos: list[dict] = field(default_factory=list)
    llamadas: list[str] = field(default_factory=list)
    ultimos_productos: list[ItemCatalogoPublico] = field(default_factory=list)
    derivada: bool = False

    @property
    def organizacion_id(self) -> uuid.UUID:
        return self.conversacion.organizacion_id

    def _monto(self, valor: Decimal | None) -> str:
        if valor is not None:
            self.montos_permitidos.add(Decimal(valor))
        return formatear(valor, self.moneda)

    def _producto(self, p: ItemCatalogoPublico) -> dict:
        return {
            "producto_id": str(p.id),
            "nombre": p.nombre,
            "precio": self._monto(p.precio_venta),
            "disponibles": p.disponibles,
            "especificaciones": p.especificaciones,
            "descripcion": (p.descripcion or "")[:300],
        }

    def _mostrar(self, productos: list[ItemCatalogoPublico]) -> None:
        if not productos:
            return  # una búsqueda vacía no borra lo que el comprador ya vio
        self.ultimos_productos = productos
        for p in productos[:3]:
            adjunto = {"tipo": "producto", "producto_id": str(p.id)}
            if p.foto_ids:
                adjunto["foto_id"] = str(p.foto_ids[0])
            if adjunto not in self.adjuntos:
                self.adjuntos.append(adjunto)

    async def ejecutar(self, nombre: str, argumentos: dict) -> dict:
        """Ejecuta un sub-agente. Nunca lanza: los errores vuelven como {"error": ...} para que la IA los explique."""
        if nombre not in NOMBRES:
            return {"error": "Herramienta desconocida."}
        self.llamadas.append(nombre)
        try:
            return await getattr(self, f"_{nombre}")(**argumentos)
        except venta.VentaError as error:
            return {"error": str(error)}
        except TypeError:
            return {"error": "Argumentos inválidos."}

    async def _buscar_productos(self, consulta: str) -> dict:
        encontrados = await stock.buscar(self.db_session, self.organizacion_id, limpiar_dato(consulta, 200))
        self._mostrar(encontrados)
        return {"productos": [self._producto(p) for p in encontrados]}

    async def _ver_catalogo(self) -> dict:
        productos = await stock.listar(self.db_session, self.organizacion_id)
        if productos:
            self.ultimos_productos = productos
        return {"productos": [self._producto(p) for p in productos]}

    async def _cotizar_envio(self, zona: str | None = None) -> dict:
        r = await envios.cotizar(self.db_session, self.organizacion_id, limpiar_dato(zona, 120) if zona else None)
        if "zona" in r:
            return {"zona": r["zona"].nombre, "costo_estimado": self._monto(r["zona"].precio), "notas": r["zona"].notas}
        if "zonas" in r:
            return {"zonas": [{"zona": z.nombre, "costo_estimado": self._monto(z.precio)} for z in r["zonas"]]}
        return {"sin_tarifas": True, "nota": "El vendedor confirma el costo del envío."}

    async def _armar_pedido(
        self, items: list[dict], zona: str | None = None, nombre_comprador: str | None = None, direccion: str | None = None
    ) -> dict:
        try:
            lineas = [(uuid.UUID(str(i["producto_id"])), int(i["cantidad"])) for i in items]
        except (KeyError, ValueError, TypeError):
            return {"error": "No entendí qué productos querés."}
        zona_elegida = None
        if zona:
            r = await envios.cotizar(self.db_session, self.organizacion_id, limpiar_dato(zona, 120))
            zona_elegida = r.get("zona")
        resultado = await venta.armar_pedido(
            self.db_session, self.conversacion, lineas, zona_elegida,
            limpiar_dato(nombre_comprador, 120) or None, limpiar_dato(direccion, 300) or None, self.simulado,
        )
        p = resultado.pedido
        if resultado.qr_id:
            self.adjuntos.append({"tipo": "qr", "qr_id": str(resultado.qr_id)})
        return {
            "pedido": [f"{i['cantidad']} × {i['nombre']} ({self._monto(Decimal(i['precio_unitario']))} c/u)" for i in p.items],
            "subtotal": self._monto(p.subtotal),
            "envio": self._monto(p.costo_envio) if p.zona_envio else "a confirmar por el vendedor",
            "total": self._monto(p.total),
            "estado": p.estado,
            "qr_enviado": bool(resultado.qr_id),
            "reserva_minutos": int((p.reservado_hasta - p.creado_en).total_seconds() // 60) if p.reservado_hasta and p.creado_en else None,
        }

    async def _informar_pago(self) -> dict:
        pedido = await venta.informar_pago(self.db_session, self.conversacion)
        if pedido is None:
            return {"error": "No hay un pedido esperando pago en esta conversación."}
        return {"ok": True, "total": self._monto(pedido.total), "nota": "El vendedor revisa su cuenta y confirma."}

    async def _derivar_a_persona(self, motivo: str) -> dict:
        await derivar_a_persona(self.db_session, self.conversacion, limpiar_dato(motivo, 300))
        self.derivada = True
        return {"ok": True}
