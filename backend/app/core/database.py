"""Database engine and session management (PostgreSQL + pgvector).

Provides a single async SQLAlchemy engine for the whole application and a
FastAPI dependency (``get_db_session``) to obtain a scoped session per
request. No business schema is defined here yet — that belongs to
``docs/006-BaseDatos`` and ``app/models`` once it starts.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

# `pool_pre_ping` avoids handing out dead connections after the DB restarts,
# which matters in local Docker environments where containers can recycle.
engine: AsyncEngine = create_async_engine(settings.database_url_async, pool_pre_ping=True)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a scoped async database session for a single request.

    Yields:
        AsyncSession: a SQLAlchemy async session, closed automatically when
        the request finishes.
    """
    async with async_session_factory() as session:
        yield session
