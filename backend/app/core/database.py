"""Database engine and session management (PostgreSQL + pgvector).

Multi-tenancy (docs/013-Seguridad/04, sección 2.2): cada sesión puede
llevar una organización en ``session.info["organizacion_id"]``. Al iniciar
CUALQUIER transacción de esa sesión (también las que se abren después de
un ``commit()``), se ejecuta ``set_config('app.organizacion_id', ..., true)``
— equivalente a ``SET LOCAL``: vale solo para esa transacción y nunca se
filtra a otro request que reciba la misma conexión del pool. Las políticas
de Row-Level Security de la base leen ese valor.
"""

import uuid
from collections.abc import AsyncGenerator

from sqlalchemy import event, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, SessionTransaction

from app.core.config import get_settings

settings = get_settings()

CLAVE_ORGANIZACION = "organizacion_id"
_SET_ORGANIZACION = text("SELECT set_config('app.organizacion_id', :org, true)")

# Pool explícito (013-04 / punto 10): pool_size + max_overflow por worker
# debe quedar por debajo de max_connections de Postgres (100 por defecto).
engine: AsyncEngine = create_async_engine(
    settings.database_url_async,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=10,
    pool_recycle=1800,
    connect_args={
        "connect_timeout": 5,
        "options": f"-c statement_timeout={settings.db_statement_timeout_ms}",
    },
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


@event.listens_for(Session, "after_begin")
def _fijar_organizacion_en_transaccion(
    session: Session, transaction: SessionTransaction, connection: Connection
) -> None:
    """Fija la organización de la sesión al empezar cada transacción."""
    organizacion_id = session.info.get(CLAVE_ORGANIZACION)
    if organizacion_id is not None:
        connection.execute(_SET_ORGANIZACION, {"org": str(organizacion_id)})


async def fijar_organizacion(session: AsyncSession, organizacion_id: uuid.UUID) -> None:
    """Asocia la sesión a una organización (RLS) desde ya y para las
    próximas transacciones.

    Args:
        session: la sesión del request.
        organizacion_id: la organización del usuario autenticado.
    """
    session.info[CLAVE_ORGANIZACION] = organizacion_id
    if session.in_transaction():
        await session.execute(_SET_ORGANIZACION, {"org": str(organizacion_id)})


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a scoped async database session for a single request."""
    async with async_session_factory() as session:
        yield session
