"""Lo que controla el dueño (docs/007-Agentes/09, sección 2): encendido, completar ventas, QR y zonas."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.atencion import AtencionConfig, QrPago, ZonaEnvio

MAX_QR = 5
MAX_ZONAS = 30


async def obtener_config(db_session: AsyncSession, organizacion_id: uuid.UUID) -> AtencionConfig:
    """La configuración de la organización; si no existe, una por defecto (apagado, sin completar ventas)."""
    config = (
        await db_session.execute(select(AtencionConfig).where(AtencionConfig.organizacion_id == organizacion_id))
    ).scalar_one_or_none()
    if config is None:
        config = AtencionConfig(
            id=uuid.uuid4(), organizacion_id=organizacion_id, encendido=False, completar_ventas=False, minutos_reserva=120
        )
    return config


async def guardar_config(db_session: AsyncSession, organizacion_id: uuid.UUID, datos: dict) -> AtencionConfig:
    config = (
        await db_session.execute(
            select(AtencionConfig).where(AtencionConfig.organizacion_id == organizacion_id).with_for_update()
        )
    ).scalar_one_or_none()
    if config is None:
        config = AtencionConfig(id=uuid.uuid4(), organizacion_id=organizacion_id)
        db_session.add(config)
    for campo, valor in datos.items():
        setattr(config, campo, valor)
    await db_session.commit()
    await db_session.refresh(config)
    return config


# ------------------------------------------------------------------ QR


async def listar_qr(db_session: AsyncSession, organizacion_id: uuid.UUID) -> list[QrPago]:
    return list(
        (
            await db_session.execute(
                select(QrPago)
                .where(QrPago.organizacion_id == organizacion_id, QrPago.eliminado_en.is_(None))
                .order_by(QrPago.creado_en)
            )
        ).scalars()
    )


class DemasiadosQrError(Exception):
    pass


async def agregar_qr(db_session: AsyncSession, organizacion_id: uuid.UUID, etiqueta: str, contenido: bytes) -> tuple[uuid.UUID, str]:
    if len(await listar_qr(db_session, organizacion_id)) >= MAX_QR:
        raise DemasiadosQrError()
    qr = QrPago(id=uuid.uuid4(), organizacion_id=organizacion_id, etiqueta=etiqueta, tipo="image/png",
                tamano=len(contenido), contenido=contenido)
    salida = (qr.id, qr.etiqueta)
    db_session.add(qr)
    await db_session.commit()
    return salida


async def obtener_qr(db_session: AsyncSession, organizacion_id: uuid.UUID, qr_id: uuid.UUID) -> QrPago | None:
    return (
        await db_session.execute(
            select(QrPago).where(QrPago.id == qr_id, QrPago.organizacion_id == organizacion_id, QrPago.eliminado_en.is_(None))
        )
    ).scalar_one_or_none()


async def qr_principal(db_session: AsyncSession, organizacion_id: uuid.UUID) -> QrPago | None:
    qrs = await listar_qr(db_session, organizacion_id)
    return qrs[0] if qrs else None


async def borrar_qr(db_session: AsyncSession, organizacion_id: uuid.UUID, qr_id: uuid.UUID) -> bool:
    qr = await obtener_qr(db_session, organizacion_id, qr_id)
    if qr is None:
        return False
    qr.eliminado_en = datetime.now(timezone.utc)  # lógico: pedidos viejos lo referencian
    await db_session.commit()
    return True


# ------------------------------------------------------------------ zonas


async def listar_zonas(db_session: AsyncSession, organizacion_id: uuid.UUID) -> list[ZonaEnvio]:
    return list(
        (
            await db_session.execute(
                select(ZonaEnvio)
                .where(ZonaEnvio.organizacion_id == organizacion_id, ZonaEnvio.eliminado_en.is_(None))
                .order_by(ZonaEnvio.nombre)
            )
        ).scalars()
    )


async def reemplazar_zonas(
    db_session: AsyncSession, organizacion_id: uuid.UUID, zonas: list[tuple[str, Decimal, str | None]]
) -> list[ZonaEnvio]:
    """Reemplaza la lista completa (las viejas quedan con borrado lógico)."""
    ahora = datetime.now(timezone.utc)
    for vieja in await listar_zonas(db_session, organizacion_id):
        vieja.eliminado_en = ahora
    db_session.add_all(
        [ZonaEnvio(id=uuid.uuid4(), organizacion_id=organizacion_id, nombre=n, precio=p, notas=x) for n, p, x in zonas]
    )
    await db_session.commit()
    return await listar_zonas(db_session, organizacion_id)
