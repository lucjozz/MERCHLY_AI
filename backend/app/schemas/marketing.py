"""Pydantic schemas para el Agente de Marketing.

Replican exactamente las secciones 2 y 3 del contrato técnico:
``docs/007-Agentes/06-Agente-de-Marketing.md``.
"""

import re
import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator

_ISO_639_1 = re.compile(r"^[a-z]{2}$")


class CanalMarketing(str, Enum):
    """Canales publicitarios soportados (contrato, sección 2)."""

    BUSQUEDA_PAGA = "busqueda_paga"
    REDES_SOCIALES = "redes_sociales"
    EMAIL = "email"


class TonoMarketing(str, Enum):
    """Tonos de campaña soportados (contrato, sección 2)."""

    NEUTRAL = "neutral"
    ENTUSIASTA = "entusiasta"
    TECNICO = "tecnico"
    PREMIUM = "premium"


class MarketingInput(BaseModel):
    """Entrada de una solicitud de campaña (contrato, sección 2).

    Attributes:
        productos_candidato_ids: productos ya aprobados a promocionar
            (entre 1 y 10). La validación de que existan y estén en
            estado 'en_catalogo' ocurre en el servicio, no aquí, porque
            requiere consultar la base de datos.
        canales_objetivo: al menos un canal de la lista soportada.
        idioma_destino: código ISO 639-1 de 2 letras.
        tono: tono de la campaña.
        presupuesto_mensual_referencia: solo para dimensionar la
            propuesta; nunca implica ejecución de gasto real.
    """

    productos_candidato_ids: list[uuid.UUID] = Field(min_length=1, max_length=10)
    canales_objetivo: list[CanalMarketing] = Field(min_length=1)
    idioma_destino: str
    tono: TonoMarketing = TonoMarketing.NEUTRAL
    presupuesto_mensual_referencia: float | None = Field(default=None, gt=0)

    @field_validator("idioma_destino")
    @classmethod
    def validar_idioma_destino(cls, valor: str) -> str:
        """Valida que sea un código ISO 639-1 (contrato, sección 2)."""
        valor_normalizado = valor.strip().lower()
        if not _ISO_639_1.match(valor_normalizado):
            raise ValueError(
                "idioma_destino debe ser un código ISO 639-1 válido "
                "(ej. 'es', 'en')."
            )
        return valor_normalizado

    @field_validator("canales_objetivo")
    @classmethod
    def validar_canales_sin_duplicados(
        cls, valor: list[CanalMarketing]
    ) -> list[CanalMarketing]:
        """Evita procesar el mismo canal dos veces por error de quien llama."""
        if len(valor) != len(set(valor)):
            raise ValueError("canales_objetivo no puede contener canales repetidos.")
        return valor


class CopyVariante(BaseModel):
    """Una variante de copy publicitario para un canal."""

    titulo: str
    cuerpo: str


class MarketingMetadata(BaseModel):
    """Metadata de una campaña generada."""

    idioma_destino: str
    tono: TonoMarketing
    fecha_generacion: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    campana_id: uuid.UUID = Field(default_factory=uuid.uuid4)


class MarketingOutput(BaseModel):
    """Salida completa de una solicitud de campaña (contrato, sección 3)."""

    productos_candidato_ids: list[uuid.UUID]
    angulos_de_campana: list[str] = Field(default_factory=list)
    copy_por_canal: dict[CanalMarketing, list[CopyVariante]] = Field(default_factory=dict)
    publico_objetivo_sugerido: str = ""
    distribucion_presupuesto_sugerida: dict[CanalMarketing, float] | None = None
    advertencias: list[str] = Field(default_factory=list)
    metadata: MarketingMetadata
