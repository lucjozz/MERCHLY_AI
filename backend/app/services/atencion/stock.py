"""Sub-agente Catálogo/Stock (docs/007-Agentes/09, sección 3.3).

Busca SOLO en el catálogo público (nunca costo ni stock real). Búsqueda
determinística por palabras sobre nombre, especificaciones y descripción:
"taladro de 800 W" encuentra "Taladro percutor 800W Pro". La búsqueda
semántica con pgvector se suma cuando haya claves de IA (embeddings).
"""

import re
import unicodedata
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.inventario import ItemCatalogoPublico
from app.services.inventario import catalogo_publico

PALABRAS_VACIAS = {
    "de", "del", "la", "el", "los", "las", "un", "una", "unos", "unas", "y", "o", "a", "en", "con", "para", "por",
    "que", "q", "tenes", "tienen", "tiene", "tienes", "hay", "busco", "quiero", "precio", "cuanto", "cuesta", "sale",
    "vale", "me", "mi", "te", "algun", "alguna", "algo", "como", "es", "esta", "este", "esa", "ese", "hola", "buenas",
    "disponible", "venden", "vendes", "favor", "porfa", "info", "informacion", "sobre",
}


def normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()
    sin_tildes = re.sub(r"(\d)\s+(w|v|kg|g|l|ml|cm|mm|m|gb|tb|mah|hp)\b", r"\1\2", sin_tildes)  # "800 w" → "800w"
    return re.sub(r"[^a-z0-9 ]+", " ", sin_tildes)


def palabras(texto: str) -> list[str]:
    salida = []
    for p in normalizar(texto).split():
        if p in PALABRAS_VACIAS or len(p) < 2:
            continue
        salida.append(p[:-1] if len(p) > 4 and p.endswith("s") else p)  # plural simple
    return salida


def _puntaje(consulta: list[str], producto: ItemCatalogoPublico) -> int:
    nombre = normalizar(producto.nombre)
    specs = normalizar(" ".join(f"{k} {v}" for k, v in producto.especificaciones.items()))
    descripcion = normalizar(producto.descripcion or "")
    puntos = 0
    for p in consulta:
        if p in nombre:
            puntos += 3
        elif p in specs:
            puntos += 2
        elif p in descripcion:
            puntos += 1
    return puntos


async def buscar(
    db_session: AsyncSession, organizacion_id: uuid.UUID, consulta: str, maximo: int = 3
) -> list[ItemCatalogoPublico]:
    terminos = palabras(consulta)
    if not terminos:
        return []
    catalogo = await catalogo_publico(db_session, organizacion_id)
    puntuados = [(p, _puntaje(terminos, p)) for p in catalogo]
    mejores = sorted([x for x in puntuados if x[1] > 0], key=lambda x: (-x[1], x[0].nombre))
    if not mejores:
        return []
    tope = mejores[0][1]
    # Solo los que están cerca del mejor: "taladro" no devuelve una linterna porque compartan "800".
    return [p for p, puntos in mejores if puntos >= max(tope - 2, 1)][:maximo]


async def listar(db_session: AsyncSession, organizacion_id: uuid.UUID, maximo: int = 10) -> list[ItemCatalogoPublico]:
    return (await catalogo_publico(db_session, organizacion_id))[:maximo]


async def por_id(
    db_session: AsyncSession, organizacion_id: uuid.UUID, producto_id: uuid.UUID
) -> ItemCatalogoPublico | None:
    return next((p for p in await catalogo_publico(db_session, organizacion_id) if p.id == producto_id), None)
