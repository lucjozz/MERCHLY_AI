"""Dependencias compartidas de FastAPI (docs/013-Seguridad/03-...)."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import decodificar_token
from app.models.usuario import Usuario

security_scheme = HTTPBearer()


async def obtener_usuario_autenticado(
    credenciales: HTTPAuthorizationCredentials = Depends(security_scheme),
    db_session: AsyncSession = Depends(get_db_session),
) -> Usuario:
    """Valida el token JWT y confirma que el usuario existe y está activo.

    Es la única pieza que los tests necesitan reemplazar (vía
    app.dependency_overrides) para simular un login sin token real — el
    chequeo de rol de requiere_rol() sigue corriendo de verdad encima.
    """
    claims = decodificar_token(credenciales.credentials)

    if claims is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
        )

    usuario = await db_session.get(Usuario, claims["sub"])

    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
        )

    return usuario


def requiere_rol(*roles_permitidos: str):
    """Crea una dependencia que exige uno de los roles indicados.

    Args:
        *roles_permitidos: los roles que pueden llamar al endpoint (ver
            docs/013-Seguridad/02-Roles-y-Permisos.md, matriz).

    Returns:
        Una función de dependencia lista para usar con Depends().
    """

    async def _verificar(
        usuario: Usuario = Depends(obtener_usuario_autenticado),
    ) -> Usuario:
        """Confirma que el rol del usuario ya autenticado esté permitido."""
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tenés permiso para realizar esta acción.",
            )

        return usuario

    return _verificar