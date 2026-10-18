"""Servicio de autenticación: valida credenciales y busca usuarios."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verificar_password
from app.models.usuario import Usuario


async def autenticar_usuario(
    db_session: AsyncSession, email: str, password: str
) -> Usuario | None:
    """Valida email y contraseña, y confirma que el usuario esté activo.

    Args:
        db_session: sesión async de SQLAlchemy.
        email: el email ingresado.
        password: la contraseña ingresada, en texto plano.

    Returns:
        Usuario | None: el usuario si las credenciales son válidas y está
        activo. None en cualquier otro caso (contrato, sección 4.1: el
        mismo resultado para "no existe", "contraseña incorrecta" o
        "inactivo" — no se distingue el motivo).
    """
    consulta = select(Usuario).where(Usuario.email == email)
    resultado = await db_session.execute(consulta)
    usuario = resultado.scalar_one_or_none()

    if usuario is None:
        return None
    if not usuario.activo:
        return None
    if not verificar_password(password, usuario.password_hash):
        return None

    return usuario