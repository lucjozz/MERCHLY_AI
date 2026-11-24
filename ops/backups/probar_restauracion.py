"""Simulacro de restauración en un entorno LIMPIO (docs/006-BaseDatos/04, sección 2.4).

1. Descifra el backup más reciente (o el indicado con --archivo).
2. Levanta un Postgres temporal NUEVO (misma imagen, sin puertos publicados).
3. Restaura ahí el backup.
4. Compara la cantidad de filas de cada tabla contra la base real.
5. Verifica que RLS sigue activo en las tablas de negocio.
6. Mide el tiempo total (RTO del simulacro) y borra el contenedor temporal.

Uso (desde la raíz del repo):
    backend\\venv\\Scripts\\python.exe ops\\backups\\probar_restauracion.py
"""

import argparse
import secrets
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backup import CONTENEDOR, clave_desde_env, descifrar, leer_env  # noqa: E402

IMAGEN = "pgvector/pgvector:pg16"
TABLAS_RLS = (
    "productos_candidatos", "decision_records", "campanas", "eventos_auditoria",
    "inventario_productos", "inventario_fotos", "atencion_config", "qr_pagos", "zonas_envio",
    "conversaciones", "mensajes", "pedidos", "notificaciones",
)


def sh(*args: str, entrada: bytes | None = None, chequear: bool = True) -> str:
    r = subprocess.run(list(args), input=entrada, capture_output=True, check=False)
    if chequear and r.returncode != 0:
        raise RuntimeError(f"{' '.join(args[:4])}…: {r.stderr.decode(errors='replace')[:400]}")
    return r.stdout.decode(errors="replace")


def conteos(contenedor: str) -> dict[str, int]:
    tablas = sh("docker", "exec", contenedor, "psql", "-U", "merchly", "-d", "merchly", "-At", "-c",
                "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY 1").split()
    resultado = {}
    for tabla in tablas:
        # Como superusuario dueño: sin filtro de RLS para el conteo administrativo.
        n = sh("docker", "exec", contenedor, "psql", "-U", "merchly", "-d", "merchly", "-At", "-c",
               f'SET row_security = off; SELECT count(*) FROM "{tabla}"').split()[-1]
        resultado[tabla] = int(n)
    return resultado


def main(archivo: Path | None) -> None:
    env = leer_env()
    clave = clave_desde_env(env)
    directorio = Path(env.get("BACKUP_DIR") or Path.home() / "Documents" / "MERCHLY_backups" / "cifrados")
    if archivo is None:
        candidatos = sorted(directorio.glob("merchly_*.dump.enc"), key=lambda p: p.stat().st_mtime)
        if not candidatos:
            sys.exit(f"No hay backups en {directorio}. Corré primero ops/backups/backup.py")
        archivo = candidatos[-1]

    inicio = time.perf_counter()
    volcado = descifrar(archivo.read_bytes(), clave)
    print(f"1. Descifrado OK: {archivo.name} ({len(volcado) // 1024} KB)")

    temporal = f"merchly-restore-{secrets.token_hex(3)}"
    clave_pg = secrets.token_urlsafe(16)
    sh("docker", "run", "-d", "--rm", "--name", temporal, "-e", "POSTGRES_USER=merchly",
       "-e", f"POSTGRES_PASSWORD={clave_pg}", "-e", "POSTGRES_DB=merchly", IMAGEN)
    try:
        # La imagen oficial arranca un servidor de inicialización y lo reinicia:
        # se espera a que acepte consultas 3 veces seguidas.
        seguidas = 0
        for _ in range(90):
            ok = subprocess.run(
                ["docker", "exec", temporal, "psql", "-U", "merchly", "-d", "merchly", "-Atc", "SELECT 1"],
                capture_output=True,
            ).returncode == 0
            seguidas = seguidas + 1 if ok else 0
            if seguidas >= 3:
                break
            time.sleep(1)
        else:
            raise RuntimeError("El Postgres temporal no quedó listo a tiempo")
        print(f"2. Postgres temporal y limpio levantado: {temporal}")

        # El rol de la app existe a nivel de cluster, no viaja en el dump.
        sh("docker", "exec", temporal, "psql", "-U", "merchly", "-d", "merchly", "-c",
           "CREATE ROLE merchly_app NOLOGIN NOSUPERUSER NOBYPASSRLS")
        sh("docker", "exec", "-i", temporal, "pg_restore", "-U", "merchly", "-d", "merchly", "--exit-on-error",
           entrada=volcado)
        print("3. Restauración OK")

        original, restaurada = conteos(CONTENEDOR), conteos(temporal)
        diferencias = {t: (original.get(t), restaurada.get(t)) for t in original if original.get(t) != restaurada.get(t)}
        if diferencias:
            # El backup es una foto de un momento: si hubo escrituras después, puede diferir.
            print(f"4. ATENCIÓN, diferencias de filas (original, restaurada): {diferencias}")
        else:
            print(f"4. Filas idénticas en las {len(original)} tablas: {original}")

        rls = sh("docker", "exec", temporal, "psql", "-U", "merchly", "-d", "merchly", "-At", "-c",
                 "SELECT relname || ':' || relrowsecurity || '/' || relforcerowsecurity FROM pg_class "
                 f"WHERE relname IN ({', '.join(repr(t) for t in TABLAS_RLS)})").split()
        if len(rls) != len(TABLAS_RLS) or not all(x.endswith(":true/true") for x in rls):
            raise RuntimeError(f"RLS no quedó activo tras restaurar: {rls}")
        print(f"5. RLS sigue activo y forzado: {', '.join(rls)}")
        print(f"6. Tiempo total del simulacro (RTO): {time.perf_counter() - inicio:.1f} s")
    finally:
        subprocess.run(["docker", "rm", "-f", temporal], capture_output=True)
        print(f"Contenedor temporal {temporal} eliminado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--archivo", type=Path, help="backup cifrado a probar (por defecto, el más reciente)")
    main(parser.parse_args().archivo)
