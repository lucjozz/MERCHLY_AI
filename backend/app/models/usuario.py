import uuid 

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ConMarcaDeTiempo

ROLES_VALIDOS = (
    "admin_principal",
    "responsable_tecnico",
    "responsable_negocio",
    "usuario_operativo",
)

class Usuario(ConMarcaDeTiempo, Base):
    """Un usuario humano del sistema (docs/013-Seguridad/01-..., sección 1).

    Attributes:
        email: identificador de login, único.
        password_hash: hash bcrypt de la contraseña. Nunca se guarda ni se
            loguea la contraseña en texto plano.
        nombre: nombre para mostrar.
        rol: uno de los 4 roles definidos en 02-Roles-y-Permisos.md.
        activo: un usuario inactivo no puede autenticarse, aunque su
            contraseña sea correcta. Reemplaza el borrado físico para
            revocar acceso sin perder el historial de decisiones que tomó.
    """

    __tablename__ = "usuarios"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    rol: Mapped[str] = mapped_column(String(30), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)