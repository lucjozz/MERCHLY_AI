"""Application configuration.

Centralizes environment-based settings for the backend service, following
the stack defined in ``docs/002-CTO/03-Stack-Tecnico.md``.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables.

    Attributes:
        app_name: Human-readable name of the service, shown in /health.
        app_version: Semantic version of the backend service.
        environment: Deployment environment (local, staging, production).
        database_url: Connection string for PostgreSQL + pgvector.
        redis_url: Connection string for Redis.
        gemini_api_key: API key for Google Gemini (Investigador IA
            provider, see docs/100-Organizacion/06-Agentes-IA.md). None
            in local/dev environments where only the simulated provider
            is used.
        gemini_model: Gemini model name used by ProveedorInvestigacionGemini.
    """

    app_name: str = "MERCHLY AI Backend"
    app_version: str = "0.1.0"
    environment: str = "local"
    database_url: str = "postgresql://merchly:merchly@db:5432/merchly"
    redis_url: str = "redis://redis:6379/0"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url_async(self) -> str:
        """Return ``database_url`` rewritten for SQLAlchemy's async psycopg driver.

        Returns:
            str: the same connection string with the ``postgresql+psycopg://``
            scheme, required by ``create_async_engine`` when using psycopg 3.
        """
        if self.database_url.startswith("postgresql+psycopg://"):
            return self.database_url
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of the application settings.

    Returns:
        Settings: the loaded configuration, cached for the process lifetime.
    """
    return Settings()
