"""Base para schemas de ENTRADA (docs/013-Seguridad/04, sección 5).

``extra="forbid"``: un campo que el cliente no debería mandar (``rol``,
``estado``, ``user_id``, ``organizacion_id``...) produce 422 en vez de
ignorarse en silencio (protección contra mass assignment).
``str_strip_whitespace``: quita espacios de los extremos.
"""

from pydantic import BaseModel, ConfigDict


class EntradaEstricta(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
