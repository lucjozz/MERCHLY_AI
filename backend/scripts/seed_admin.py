"""Alta y rotación de usuarios admin (docs/013-Seguridad/04, sección 3.2).

La contraseña se pide con getpass: NO se ve en pantalla ni queda en el
historial de la terminal. Se valida la política (12+ caracteres, <= 72 bytes).

Uso (desde la carpeta raíz del repo, con los contenedores levantados):
    docker compose exec backend python -m scripts.seed_admin            # crear admin
    docker compose exec backend python -m scripts.seed_admin --rotar    # cambiar contraseña

Rotar la contraseña también cierra todas las sesiones abiertas de ese usuario.
"""

import argparse
import asyncio
import getpass
import sys
import uuid

from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import PasswordInvalidaError, hashear_password
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario
from app.services.autenticacion import cerrar_todas_las_sesiones

ORG_INICIAL = "MERCHLY (organización inicial)"


def _pedir_password() -> str:
    while True:
        p1 = getpass.getpass("Contraseña nueva (no se ve al escribir): ")
        p2 = getpass.getpass("Repetila: ")
        if p1 != p2:
            print("No coinciden. Probá de nuevo.")
            continue
        try:
            return hashear_password(p1)
        except PasswordInvalidaError as error:
            print(error)


async def crear() -> None:
    email = input("Email del admin: ").strip().lower()
    nombre = input("Nombre: ").strip()[:120] or "Admin"
    nombre_org = input(f"Organización [{ORG_INICIAL}]: ").strip()[:120] or ORG_INICIAL
    password_hash = _pedir_password()

    async with async_session_factory() as s:
        if (await s.execute(select(Usuario).where(Usuario.email == email))).scalar_one_or_none():
            print("Ese email ya existe. Usá --rotar para cambiarle la contraseña.")
            return
        org = (await s.execute(select(Organizacion).where(Organizacion.nombre == nombre_org))).scalar_one_or_none()
        if org is None:
            org = Organizacion(id=uuid.uuid4(), nombre=nombre_org)
            s.add(org)
            await s.flush()
        s.add(
            Usuario(
                id=uuid.uuid4(),
                organizacion_id=org.id,
                email=email,
                password_hash=password_hash,
                nombre=nombre,
                rol="admin_principal",
                activo=True,
                token_version=0,
            )
        )
        await s.commit()
    print(f"Listo: {email} es admin_principal de '{nombre_org}'.")


async def rotar() -> None:
    email = input("Email del usuario: ").strip().lower()
    async with async_session_factory() as s:
        usuario = (await s.execute(select(Usuario).where(Usuario.email == email))).scalar_one_or_none()
        if usuario is None:
            print("No existe ese usuario.")
            return
        usuario.password_hash = _pedir_password()
        await cerrar_todas_las_sesiones(s, usuario)  # hace commit
    print("Contraseña cambiada y todas las sesiones de ese usuario cerradas.")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rotar", action="store_true", help="cambiar la contraseña de un usuario existente")
    asyncio.run(rotar() if parser.parse_args().rotar else crear())
