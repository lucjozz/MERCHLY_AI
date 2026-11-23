"""Límites de uso y revocación de tokens sobre Redis (013-04, secciones 3 y 4).

Sin FastAPI: los endpoints deciden qué hacer si Redis falla
(login = fail-closed, agentes = fail-open). Las funciones dejan pasar la
``RedisError`` para que el llamador elija.

Patrón de contador con ventana: ``SET clave 0 EX ventana NX`` + ``INCR``.
El TTL se fija una sola vez al crear la clave (atómico) y el INCR nunca lo
renueva, así que la ventana no se "estira" con cada intento.
"""

import hashlib

from redis.asyncio import Redis
from redis.exceptions import RedisError

__all__ = ["RedisError", "LimitesLogin", "consumir_cuota", "revocar_jti", "jti_revocado"]


def _hash(*partes: str) -> str:
    """Las claves no guardan emails ni IPs en claro."""
    return hashlib.sha256("|".join(partes).encode("utf-8")).hexdigest()[:32]


async def _incrementar(redis: Redis, clave: str, ventana: int) -> int:
    await redis.set(clave, 0, ex=ventana, nx=True)
    return int(await redis.incr(clave))


async def _ttl(redis: Redis, clave: str, ventana: int) -> int:
    ttl = int(await redis.ttl(clave))
    return ttl if ttl > 0 else ventana


class LimitesLogin:
    """Bloqueo de login por (email, IP), por IP y por email.

    El límite por email (independiente de la IP) frena ataques distribuidos
    contra una cuenta desde muchas IPs; es más alto que el de email+IP para
    que un tercero no pueda bloquear fácilmente a un usuario legítimo.
    """

    def __init__(
        self, redis: Redis, max_email_ip: int, max_ip: int, ventana: int, max_email: int | None = None
    ) -> None:
        self.redis = redis
        self.max_email_ip = max_email_ip
        self.max_ip = max_ip
        self.max_email = max_email if max_email is not None else max_email_ip * 2
        self.ventana = ventana

    def _claves(self, email: str, ip: str) -> tuple[str, str, str]:
        return (
            f"login:fallos:ei:{_hash(email, ip)}",
            f"login:fallos:ip:{_hash(ip)}",
            f"login:fallos:e:{_hash(email)}",
        )

    async def segundos_bloqueado(self, email: str, ip: str) -> int:
        """0 si puede intentar; si no, los segundos que faltan (Retry-After)."""
        claves = self._claves(email, ip)
        valores = [int(v or 0) for v in await self.redis.mget(*claves)]
        for clave, fallos, maximo in zip(claves, valores, (self.max_email_ip, self.max_ip, self.max_email)):
            if fallos >= maximo:
                return await _ttl(self.redis, clave, self.ventana)
        return 0

    async def registrar_fallo(self, email: str, ip: str) -> None:
        for clave in self._claves(email, ip):
            await _incrementar(self.redis, clave, self.ventana)

    async def limpiar(self, email: str, ip: str) -> None:
        """Un login correcto limpia los contadores de ese email (no el de la IP)."""
        clave_ei, _, clave_e = self._claves(email, ip)
        await self.redis.delete(clave_ei, clave_e)


async def consumir_cuota(redis: Redis, nombre: str, sujeto: str, limite: int, ventana: int) -> int:
    """Consume una unidad de cuota.

    Returns:
        int: 0 si había cuota; si no, segundos hasta que se renueve.
    """
    clave = f"cuota:{nombre}:{_hash(sujeto)}"
    usados = await _incrementar(redis, clave, ventana)
    if usados > limite:
        return await _ttl(redis, clave, ventana)
    return 0


async def revocar_jti(redis: Redis, jti: str, segundos_restantes: int) -> None:
    """Agrega el jti a la denylist hasta que el token hubiera vencido solo."""
    if segundos_restantes > 0:
        await redis.set(f"jwt:revocado:{jti}", 1, ex=segundos_restantes)


async def jti_revocado(redis: Redis, jti: str) -> bool:
    return bool(await redis.exists(f"jwt:revocado:{jti}"))
