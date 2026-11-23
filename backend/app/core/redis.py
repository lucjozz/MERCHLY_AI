"""Redis client management.

Un solo cliente async para toda la app, con timeouts cortos: si Redis no
responde, preferimos fallar rápido (y aplicar fail-open/fail-closed según
013-04, sección 4) antes que colgar el request.
"""

from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()

redis_client: Redis = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_timeout=2,
    socket_connect_timeout=2,
    health_check_interval=30,
)


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """Yield the shared async Redis client."""
    yield redis_client
