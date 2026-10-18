"""Endpoints de autenticación (docs/013-Seguridad/01-...)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencias import obtener_usuario_autenticado
from app.core.security import crear_token
from app.models.usuario import Usuario
from app.schemas.auth import LoginInput, LoginOutput, UsuarioActual
from app.services.autenticacion import autenticar_usuario

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginOutput,
    status_code=status.HTTP_200_OK,
)
async def login(
    entrada: LoginInput,
    db_session: AsyncSession = Depends(get_db_session),
) -> LoginOutput:
    """Autentica un usuario y devuelve un token JWT.

    Args:
        entrada: email y contraseña.
        db_session: sesión de base de datos inyectada.

    Returns:
        LoginOutput: el token de acceso.

    Raises:
        HTTPException: 401 si las credenciales son inválidas (mismo
            mensaje sin importar el motivo exacto, contrato sección 4.1).
    """
    usuario = await autenticar_usuario(
        db_session=db_session, email=entrada.email, password=entrada.password
    )

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    token, expira_en = crear_token(
        usuario_id=str(usuario.id), email=usuario.email, rol=usuario.rol
    )

    return LoginOutput(access_token=token, expira_en=expira_en)


@router.get(
    "/me",
    response_model=UsuarioActual,
    status_code=status.HTTP_200_OK,
)
async def obtener_usuario_actual(
    usuario: Usuario = Depends(obtener_usuario_autenticado),
) -> UsuarioActual:
    """Confirma qué usuario y rol tiene el token actual (contrato, sección 4.2).

    Args:
        usuario: el usuario ya autenticado, resuelto por la dependencia.

    Returns:
        UsuarioActual: los datos del usuario autenticado.
    """
    return usuario