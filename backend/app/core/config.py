"""Application configuration.

Centralizes environment-based settings for the backend service, following
the stack defined in ``docs/002-CTO/03-Stack-Tecnico.md``. Security-related
settings follow ``docs/013-Seguridad/04-Endurecimiento-para-Lanzamiento.md``.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Valores de ejemplo conocidos públicamente: el backend se niega a arrancar
# con cualquiera de ellos (013-04, sección 3).
SECRETOS_DE_EJEMPLO = frozenset(
    {"cambiar-en-produccion", "changeme", "secret", "secreto", "merchly"}
)
LARGO_MINIMO_SECRETO = 32


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables.

    Attributes:
        environment: local, test, staging o production.
        database_url: conexión de la APP (rol ``merchly_app``, sin privilegios
            de dueño, sujeto a RLS).
        database_url_migraciones: conexión de Alembic (rol dueño de las
            tablas). Si no se define, se usa ``database_url``.
        jwt_secret_key: secreto HS256. El arranque falla si es débil.
        access_token_minutos / refresh_token_dias: vida de cada token.
        cors_origenes: lista separada por comas de orígenes permitidos.
        exponer_docs: muestra /docs, /redoc y /openapi.json.
        confiar_proxy: usar X-Forwarded-For / CF-Connecting-IP para la IP
            del cliente. Solo con el origen cerrado detrás del proxy.
        google_client_id: Client ID OAuth de Google (vacío = deshabilitado).
    """

    app_name: str = "MERCHLY AI Backend"
    app_version: str = "0.2.0"
    environment: str = "local"
    database_url: str = "postgresql://merchly_app:merchly_app@db:5432/merchly"
    database_url_migraciones: str | None = None
    redis_url: str = "redis://redis:6379/0"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    # Valor de ejemplo: el arranque lo RECHAZA (problemas_de_seguridad).
    jwt_secret_key: str = "cambiar-en-produccion"  # noqa: S105
    jwt_issuer: str = "merchly-ai"
    jwt_audience: str = "merchly-api"
    access_token_minutos: int = 15
    refresh_token_dias: int = 14

    cors_origenes: str = "http://localhost:3000"
    exponer_docs: bool = False
    confiar_proxy: bool = False
    max_body_bytes: int = 1_048_576

    login_max_fallos_email_ip: int = 5
    login_max_fallos_ip: int = 20
    login_max_fallos_email: int = 10
    login_ventana_segundos: int = 900
    cuota_investigador_por_hora: int = 30
    cuota_marketing_por_hora: int = 60

    google_client_id: str | None = None

    # IA real (docs/007-Agentes/07). Sin clave = proveedor simulado.
    openai_api_key: str | None = None
    ia_timeout_segundos: float = 45.0
    ia_max_tokens_salida: int = 8192
    # Modelo por agente y por plan: mejor plan = mejor modelo. Configurables
    # porque los nombres de modelos cambian; se validan con scripts.probar_ia.
    modelo_investigador_beta: str = "gemini-2.5-flash-lite"
    modelo_investigador_emprendedor: str = "gemini-2.5-flash"
    modelo_investigador_negocio: str = "gemini-2.5-pro"
    modelo_marketing_beta: str = "gpt-5-nano"
    modelo_marketing_emprendedor: str = "gpt-5-mini"
    modelo_marketing_negocio: str = "gpt-5"

    db_pool_size: int = 5
    db_max_overflow: int = 5
    db_statement_timeout_ms: int = 15_000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @staticmethod
    def _a_async(url: str) -> str:
        if url.startswith("postgresql+psycopg://"):
            return url
        return url.replace("postgresql://", "postgresql+psycopg://", 1)

    @property
    def database_url_async(self) -> str:
        """``database_url`` con el esquema ``postgresql+psycopg://``."""
        return self._a_async(self.database_url)

    @property
    def database_url_migraciones_async(self) -> str:
        """URL que usa Alembic (rol dueño de las tablas)."""
        return self._a_async(self.database_url_migraciones or self.database_url)

    @property
    def lista_cors_origenes(self) -> list[str]:
        return [o.strip() for o in self.cors_origenes.split(",") if o.strip() and o.strip() != "*"]

    @property
    def es_produccion(self) -> bool:
        return self.environment in ("staging", "production")

    def problemas_de_seguridad(self) -> list[str]:
        """Devuelve los motivos por los que esta configuración no es segura.

        Se evalúa en el arranque (lifespan). Una lista vacía = OK.
        """
        problemas: list[str] = []
        secreto = self.jwt_secret_key
        if len(secreto) < LARGO_MINIMO_SECRETO or secreto.lower() in SECRETOS_DE_EJEMPLO:
            problemas.append(
                "JWT_SECRET_KEY es débil (mínimo 32 caracteres, no un valor de ejemplo). "
                "Generá uno con: python -c \"import secrets;print(secrets.token_urlsafe(64))\""
            )
        if self.es_produccion and self.exponer_docs:
            problemas.append("EXPONER_DOCS no puede estar activo en staging/producción.")
        return problemas


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of the application settings."""
    return Settings()
