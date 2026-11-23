"""Defensas comunes para proveedores de IA (docs/007-Agentes/07, sección 4).

- Entrada: los textos que vienen del usuario o de la base se limpian
  (sin caracteres de control, largo acotado) y se envían DELIMITADOS como
  datos, para que el modelo no los confunda con instrucciones
  (prompt injection).
- Salida: se recortan textos a los largos de las columnas, se descartan
  URLs que no sean http(s) y se acotan las listas, antes de persistir o
  mostrar nada.
"""

import re
import unicodedata

INICIO_DATOS = "<<<DATOS"
FIN_DATOS = "DATOS>>>"

# Caracteres de control (salvo salto de línea y tab) y separadores raros
# que se usan para esconder instrucciones.
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f​-‏ -‮⁦-⁩]")


def limpiar_dato(texto: object, maximo: int = 500) -> str:
    """Normaliza un dato no confiable para meterlo en un prompt."""
    valor = unicodedata.normalize("NFKC", str(texto or ""))
    valor = _CONTROL.sub("", valor)
    # Que el dato no pueda "cerrar" el bloque delimitado.
    valor = valor.replace(INICIO_DATOS, "").replace(FIN_DATOS, "")
    return valor.strip()[:maximo]


def bloque_de_datos(lineas: list[str]) -> str:
    """Envuelve datos no confiables entre los delimitadores del prompt."""
    return "\n".join([INICIO_DATOS, *lineas, FIN_DATOS])


def recortar(texto: object, maximo: int) -> str:
    """Recorta salida de la IA a un largo seguro para la base / la UI."""
    return _CONTROL.sub("", str(texto or "")).strip()[:maximo]


def solo_urls_http(valores: list[str], maximo_items: int = 10, largo: int = 500) -> list[str]:
    """Evidencia: se quedan solo URLs http(s) o textos planos sin esquema
    peligroso (javascript:, data:, file:...)."""
    salida: list[str] = []
    for valor in valores[: maximo_items * 2]:
        limpio = recortar(valor, largo)
        if not limpio:
            continue
        esquema = limpio.split(":", 1)[0].lower() if ":" in limpio[:12] else ""
        if esquema and esquema not in ("http", "https"):
            continue
        salida.append(limpio)
        if len(salida) >= maximo_items:
            break
    return salida


def lista_recortada(valores: list[str], maximo_items: int = 10, largo: int = 500) -> list[str]:
    return [t for t in (recortar(v, largo) for v in valores[:maximo_items]) if t]
