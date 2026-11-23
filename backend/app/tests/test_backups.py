"""Tests del backup cifrado (ops/backups/backup.py, DEC-036): cifrado y retención."""

import base64
import importlib.util
import secrets
from datetime import date
from pathlib import Path

import pytest

_RUTA = Path(__file__).resolve().parents[3] / "ops" / "backups" / "backup.py"
_spec = importlib.util.spec_from_file_location("backup_ops", _RUTA)
backup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(backup)


def test_cifrado_ida_y_vuelta_y_clave_incorrecta() -> None:
    clave = secrets.token_bytes(32)
    blob = backup.cifrar(b"datos de la base", clave)
    assert blob.startswith(backup.CABECERA) and b"datos de la base" not in blob
    assert backup.descifrar(blob, clave) == b"datos de la base"
    with pytest.raises(Exception):
        backup.descifrar(blob, secrets.token_bytes(32))  # otra clave: no se puede leer
    with pytest.raises(Exception):
        backup.descifrar(blob[:-1] + bytes([blob[-1] ^ 1]), clave)  # alterado: se detecta


def test_clave_invalida_corta_el_proceso() -> None:
    with pytest.raises(SystemExit):
        backup.clave_desde_env({"BACKUP_KEY": base64.b64encode(b"corta").decode()})
    assert len(backup.clave_desde_env({"BACKUP_KEY": base64.b64encode(b"x" * 32).decode()})) == 32


def test_tipo_de_backup_segun_el_dia() -> None:
    assert backup.tipo_de_backup(date(2026, 12, 1)) == "mensual"
    assert backup.tipo_de_backup(date(2026, 11, 29)) == "semanal"  # domingo
    assert backup.tipo_de_backup(date(2026, 11, 24)) == "diario"


def test_retencion_de_la_politica(tmp_path: Path) -> None:
    hoy = date(2026, 11, 24)
    for nombre in [
        "merchly_diario_2026-11-20T000000Z.dump.enc",   # 4 días: queda
        "merchly_diario_2026-10-01T000000Z.dump.enc",   # > 30 días: se borra
        "merchly_semanal_2026-09-06T000000Z.dump.enc",  # 11 semanas: queda
        "merchly_semanal_2026-06-07T000000Z.dump.enc",  # > 12 semanas: se borra
        "merchly_mensual_2026-01-01T000000Z.dump.enc",  # ~11 meses: queda
        "merchly_mensual_2025-10-01T000000Z.dump.enc",  # > 12 meses: se borra
        "otro_archivo.txt",                             # ajeno: no se toca
    ]:
        (tmp_path / nombre).write_bytes(b"x")
    backup.aplicar_retencion(tmp_path, hoy)
    quedan = sorted(p.name for p in tmp_path.iterdir())
    assert quedan == [
        "merchly_diario_2026-11-20T000000Z.dump.enc",
        "merchly_mensual_2026-01-01T000000Z.dump.enc",
        "merchly_semanal_2026-09-06T000000Z.dump.enc",
        "otro_archivo.txt",
    ]
