"""Fixtures y helpers compartidos por todos los tests."""

import asyncio
import sys
import uuid

import pytest

from app.models.usuario import Usuario

@pytest.fixture(scope="session")
def event_loop_policy():
    """psycopg async no funciona con el ProactorEventLoop de Windows."""
    if sys.platform == "win32":
        return asyncio.WindowsSelectorEventLoopPolicy()
    return asyncio.DefaultEventLoopPolicy()


# Organización fija para los tests unitarios (mockean la base).
ORG_TEST = uuid.UUID("00000000-0000-4000-8000-000000000001")


class RedisFalso:
    """Redis en memoria con lo mínimo que usa app.services.limites.

    No modela el paso del tiempo: los TTL se guardan pero no vencen.
    """

    def __init__(self) -> None:
        self.datos: dict[str, int] = {}
        self.ttls: dict[str, int] = {}

    async def set(self, clave, valor, ex=None, nx=False):
        if nx and clave in self.datos:
            return None
        self.datos[clave] = int(valor)
        if ex:
            self.ttls[clave] = ex
        return True

    async def incr(self, clave):
        self.datos[clave] = self.datos.get(clave, 0) + 1
        return self.datos[clave]

    async def get(self, clave):
        return self.datos.get(clave)

    async def mget(self, *claves):
        return [self.datos.get(c) for c in claves]

    async def ttl(self, clave):
        return self.ttls.get(clave, -2)

    async def delete(self, *claves):
        for c in claves:
            self.datos.pop(c, None)
            self.ttls.pop(c, None)

    async def exists(self, clave):
        return 1 if clave in self.datos else 0


class RedisCaido:
    """Redis que siempre falla (para probar fail-open / fail-closed)."""

    def __getattr__(self, _):
        from redis.exceptions import ConnectionError as RedisConnectionError

        async def _falla(*a, **k):
            raise RedisConnectionError("caído")

        return _falla


def usuario_falso(rol: str = "admin_principal", organizacion_id: uuid.UUID = ORG_TEST) -> Usuario:
    """Un usuario de mentira para tests, sin tocar la base de datos."""
    return Usuario(
        id=uuid.uuid4(),
        organizacion_id=organizacion_id,
        email="test@merchly.ai",
        password_hash="no-importa-en-tests",
        nombre="Usuario de Test",
        rol=rol,
        activo=True,
        token_version=0,
    )


def override_usuario_autenticado(rol: str = "admin_principal", organizacion_id: uuid.UUID = ORG_TEST):
    """Reemplazo de obtener_usuario_autenticado() para app.dependency_overrides.
    El chequeo de rol de requiere_rol() sigue corriendo de verdad encima."""

    usuario = usuario_falso(rol=rol, organizacion_id=organizacion_id)

    async def _override() -> Usuario:
        return usuario

    return _override
