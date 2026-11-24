"""Retención de datos: borra o anonimiza lo que ya no hace falta guardar (docs/013-Seguridad/09, sección 6).

Cumple lo que promete la Política de Privacidad (docs/021-Legal/02):
* Mensajes con compradores: 12 meses.
* Datos personales de compradores en conversaciones y pedidos viejos: se ANONIMIZAN
  a los 12 meses (los montos de los pedidos se conservan para la contabilidad).
* Avisos al vendedor: 90 días.
* Sesiones, links de recuperación e invitaciones vencidas: 30 a 90 días.
* Bitácora de seguridad: 24 meses (la política exige al menos 12).

Corre como el DUEÑO de la base (el rol de la app no puede borrar mensajes ni
la bitácora: son append-only). Por defecto solo CUENTA lo que haría.

Uso (desde la raíz del repo, con el venv del backend):
    backend\\venv\\Scripts\\python.exe ops\\retencion\\limpiar.py            # simulacro: muestra cuántas filas
    backend\\venv\\Scripts\\python.exe ops\\retencion\\limpiar.py --aplicar  # borra / anonimiza
"""

import argparse
import os
import subprocess
import sys

CONTENEDOR = os.environ.get("BACKUP_CONTENEDOR_DB", "merchly-db")

# (descripción, condición para contar, sentencia que aplica). Todo en una transacción.
REGLAS: list[tuple[str, str, str]] = [
    (
        "Mensajes de más de 12 meses",
        "SELECT count(*) FROM mensajes WHERE creado_en < now() - interval '12 months'",
        "DELETE FROM mensajes WHERE creado_en < now() - interval '12 months'",
    ),
    (
        "Conversaciones de más de 12 meses (se anonimiza el contacto)",
        "SELECT count(*) FROM conversaciones WHERE coalesce(ultimo_mensaje_en, creado_en) < now() - interval '12 months' AND contacto <> 'anonimizado'",
        "UPDATE conversaciones SET contacto = 'anonimizado', nombre_contacto = NULL "
        "WHERE coalesce(ultimo_mensaje_en, creado_en) < now() - interval '12 months' AND contacto <> 'anonimizado'",
    ),
    (
        "Pedidos de más de 12 meses (se anonimiza nombre y dirección; los montos quedan)",
        "SELECT count(*) FROM pedidos WHERE creado_en < now() - interval '12 months' AND (nombre_comprador IS NOT NULL OR direccion IS NOT NULL)",
        "UPDATE pedidos SET nombre_comprador = NULL, direccion = NULL "
        "WHERE creado_en < now() - interval '12 months' AND (nombre_comprador IS NOT NULL OR direccion IS NOT NULL)",
    ),
    (
        "Avisos de más de 90 días",
        "SELECT count(*) FROM notificaciones WHERE creado_en < now() - interval '90 days'",
        "DELETE FROM notificaciones WHERE creado_en < now() - interval '90 days'",
    ),
    (
        "Sesiones vencidas hace más de 30 días",
        "SELECT count(*) FROM refresh_tokens WHERE expira_en < now() - interval '30 days'",
        "DELETE FROM refresh_tokens WHERE expira_en < now() - interval '30 days'",
    ),
    (
        "Links de recuperación vencidos hace más de 30 días",
        "SELECT count(*) FROM restablecimientos_password WHERE expira_en < now() - interval '30 days'",
        "DELETE FROM restablecimientos_password WHERE expira_en < now() - interval '30 days'",
    ),
    (
        "Invitaciones vencidas o aceptadas hace más de 90 días",
        "SELECT count(*) FROM invitaciones WHERE coalesce(aceptada_en, expira_en) < now() - interval '90 days'",
        "DELETE FROM invitaciones WHERE coalesce(aceptada_en, expira_en) < now() - interval '90 days'",
    ),
    (
        "Bitácora de seguridad de más de 24 meses",
        "SELECT count(*) FROM eventos_auditoria WHERE creado_en < now() - interval '24 months'",
        "DELETE FROM eventos_auditoria WHERE creado_en < now() - interval '24 months'",
    ),
]


def _psql(sql: str) -> str:
    r = subprocess.run(
        ["docker", "exec", "-i", CONTENEDOR, "psql", "-U", "merchly", "-d", "merchly", "-qAt", "-v", "ON_ERROR_STOP=1"],
        input=sql, capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        sys.exit(f"Error de la base: {r.stderr.strip()[:500]}")
    return r.stdout


def script_aplicar() -> str:
    return "BEGIN;\n" + "\n".join(s + ";" for _, _, s in REGLAS) + "\nCOMMIT;\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--aplicar", action="store_true", help="borrar / anonimizar de verdad (sin esto, solo cuenta)")
    args = parser.parse_args()

    conteos = _psql("\n".join(c + ";" for _, c, _ in REGLAS)).split()
    print("Retención de datos" + ("" if args.aplicar else " (simulacro: no se cambia nada)"))
    for (descripcion, _, _), cantidad in zip(REGLAS, conteos, strict=True):
        print(f"  {cantidad:>8}  {descripcion}")
    if args.aplicar:
        _psql(script_aplicar())
        print("Listo: aplicado en una sola transacción.")
    else:
        print("Para aplicarlo: agregá --aplicar")


if __name__ == "__main__":
    main()
