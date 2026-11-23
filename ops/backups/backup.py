"""Backup cifrado de la base de MERCHLY (docs/006-BaseDatos/04, DEC-036).

Hace un pg_dump (formato custom) del contenedor de Postgres, lo cifra con
AES-256-GCM y lo guarda fuera del repo, aplicando la retención de la
política: diarios 30 días, semanales (domingo) 12 semanas, mensuales (día 1)
12 meses.

Uso (desde la raíz del repo, con el venv del backend):
    backend\\venv\\Scripts\\python.exe ops\\backups\\backup.py

Requiere en el .env de la raíz:
    BACKUP_KEY=<32 bytes en base64>   (generar con: python ops/backups/backup.py --generar-clave)
Opcional:
    BACKUP_DIR=C:\\ruta\\fuera\\del\\repo   (por defecto ~/Documents/MERCHLY_backups/cifrados)

SIN LA CLAVE NO HAY FORMA DE RECUPERAR UN BACKUP: guardala también en un
gestor de contraseñas, fuera de esta PC.
"""

import argparse
import base64
import os
import secrets
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

RAIZ = Path(__file__).resolve().parents[2]
CABECERA = b"MRCHBK1"  # formato: CABECERA + nonce(12) + cifrado(+tag)
CONTENEDOR = os.environ.get("BACKUP_CONTENEDOR_DB", "merchly-db")
RETENCION = {"diario": 30, "semanal": 7 * 12, "mensual": 31 * 12}  # en días


def leer_env() -> dict[str, str]:
    valores: dict[str, str] = {}
    archivo = RAIZ / ".env"
    if archivo.exists():
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.lstrip().startswith("#"):
                clave, valor = linea.split("=", 1)
                valores[clave.strip()] = valor.strip()
    valores.update({k: v for k, v in os.environ.items() if k.startswith("BACKUP_")})
    return valores


def clave_desde_env(env: dict[str, str]) -> bytes:
    texto = env.get("BACKUP_KEY", "")
    try:
        clave = base64.b64decode(texto, validate=True)
    except ValueError:
        clave = b""
    if len(clave) != 32:
        sys.exit("Falta BACKUP_KEY válida (32 bytes en base64) en el .env de la raíz. Generala con --generar-clave.")
    return clave


def cifrar(datos: bytes, clave: bytes) -> bytes:
    nonce = secrets.token_bytes(12)
    return CABECERA + nonce + AESGCM(clave).encrypt(nonce, datos, CABECERA)


def descifrar(blob: bytes, clave: bytes) -> bytes:
    if not blob.startswith(CABECERA):
        raise ValueError("No es un backup de MERCHLY")
    nonce = blob[len(CABECERA): len(CABECERA) + 12]
    return AESGCM(clave).decrypt(nonce, blob[len(CABECERA) + 12:], CABECERA)


def tipo_de_backup(hoy: date) -> str:
    if hoy.day == 1:
        return "mensual"
    if hoy.weekday() == 6:
        return "semanal"
    return "diario"


def aplicar_retencion(directorio: Path, hoy: date) -> list[Path]:
    borrados = []
    for archivo in directorio.glob("merchly_*_*.dump.enc"):
        try:
            _, tipo, fecha = archivo.name.removesuffix(".dump.enc").split("_", 2)
            dia = datetime.strptime(fecha[:10], "%Y-%m-%d").date()
        except ValueError:
            continue
        if tipo in RETENCION and hoy - dia > timedelta(days=RETENCION[tipo]):
            archivo.unlink()
            borrados.append(archivo)
    return borrados


def hacer_backup(env: dict[str, str]) -> Path:
    clave = clave_desde_env(env)
    directorio = Path(env.get("BACKUP_DIR") or Path.home() / "Documents" / "MERCHLY_backups" / "cifrados")
    directorio.mkdir(parents=True, exist_ok=True)
    if RAIZ in directorio.resolve().parents or directorio.resolve() == RAIZ:
        sys.exit("BACKUP_DIR no puede estar dentro del repositorio (Norma 11).")

    volcado = subprocess.run(
        ["docker", "exec", CONTENEDOR, "pg_dump", "-U", "merchly", "-d", "merchly", "-Fc", "--no-password"],
        capture_output=True,
        check=False,
    )
    if volcado.returncode != 0 or not volcado.stdout:
        sys.exit(f"pg_dump falló: {volcado.stderr.decode(errors='replace')[:300]}")

    ahora = datetime.now(timezone.utc)
    hoy = ahora.date()
    destino = directorio / f"merchly_{tipo_de_backup(hoy)}_{ahora:%Y-%m-%dT%H%M%SZ}.dump.enc"
    destino.write_bytes(cifrar(volcado.stdout, clave))
    borrados = aplicar_retencion(directorio, hoy)
    print(f"Backup OK: {destino} ({destino.stat().st_size // 1024} KB cifrado)")
    if borrados:
        print(f"Retención: se borraron {len(borrados)} backups vencidos.")
    return destino


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--generar-clave", action="store_true", help="imprime una clave nueva para BACKUP_KEY")
    args = parser.parse_args()
    if args.generar_clave:
        print(base64.b64encode(secrets.token_bytes(32)).decode())
    else:
        hacer_backup(leer_env())
