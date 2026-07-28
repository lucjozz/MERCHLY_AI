"""Redis client management.

Provides a single async Redis client for the whole application and a
FastAPI dependency (``get_redis_client``) to inject it where needed.
"""

from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()

redis_client: Redis = Redis.from_url(settings.redis_url, decode_responses=True)


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """Yield the shared async Redis client.

    Yields:
        Redis: the application-wide Redis client instance.
    """
    yield redis_client
