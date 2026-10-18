"""Script de seed: crea el primer usuario admin_principal (Lucas).

Uso: python scripts/seed_admin.py
Ver docs/013-Seguridad/01-Modelo-de-Usuarios-y-Autenticacion.md, sección 1.
"""

import asyncio
import sys
import uuid

import bcrypt

from app.core.database import async_session_factory
from app.models.usuario import Usuario


async def crear_admin() -> None:
    """Crea el usuario admin_principal si todavía no existe."""
    email = input("Email del admin: ").strip()
    nombre = input("Nombre: ").strip()
    password = input("Contraseña: ").strip()

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt(rounds=12)
    ).decode("utf-8")

    async with async_session_factory() as session:
        usuario = Usuario(
            id=uuid.uuid4(),
            email=email,
            password_hash=password_hash,
            nombre=nombre,
            rol="admin_principal",
            activo=True,
        )
        session.add(usuario)
        await session.commit()
        print(f"Usuario creado: {email} (admin_principal)")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(crear_admin())