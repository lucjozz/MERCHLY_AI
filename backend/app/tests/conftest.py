"""Fixtures y helpers compartidos por todos los tests (pytest los detecta
automáticamente en este archivo, sin necesidad de import explícito)."""

import uuid

from app.models.usuario import Usuario


def usuario_falso(rol: str = "admin_principal") -> Usuario:
    """Crea un usuario de mentira para tests, sin tocar la base de datos.

    Args:
        rol: el rol a simular (default: el de mayor privilegio).

    Returns:
        Usuario: un objeto que se comporta como un usuario real, para
        pasarlo directo a un endpoint sin pasar por login de verdad.
    """
    return Usuario(
        id=uuid.uuid4(),
        email="test@merchly.ai",
        password_hash="no-importa-en-tests",
        nombre="Usuario de Test",
        rol=rol,
        activo=True,
    )


def override_usuario_autenticado(rol: str = "admin_principal"):
    """Reemplazo de obtener_usuario_autenticado(), para usar con
    app.dependency_overrides — simula un login exitoso sin token real.
    El chequeo de rol de requiere_rol() sigue corriendo de verdad encima
    de este override, así que los tests de 403 siguen siendo reales.

    Args:
        rol: qué rol tiene el usuario de mentira devuelto.

    Returns:
        Una función de dependencia que devuelve un usuario falso directo.
    """

    async def _override() -> Usuario:
        return usuario_falso(rol=rol)

    return _override