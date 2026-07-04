"""
Application Settings
====================
Single source of truth for all platform configuration.

All values can be overridden via environment variables or a ``.env`` file.
No configuration value is ever hard-coded in application code.

Future modules (LLM, AWS, PostgreSQL) will add their own fields here
when those sprints begin. The ``Settings`` class is intentionally flat —
no nested sub-settings classes until the complexity justifies it.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Platform-wide application settings.

    Loaded once at startup and cached for the process lifetime.
    Access via ``get_settings()`` — never instantiate directly in application code.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ------------------------------------------------------------------
    # Application identity
    # ------------------------------------------------------------------
    app_name: str = Field(
        default="Enterprise Intelligent Incident Diagnosis Platform",
        description="Human-readable application name shown in API docs",
    )
    app_version: str = Field(default="1.0.0", description="Semantic version string")
    app_description: str = Field(
        default=(
            "AI-powered platform that transforms raw application logs "
            "into structured, explainable incident diagnoses."
        ),
        description="Application description shown in OpenAPI docs",
    )

    # ------------------------------------------------------------------
    # Runtime environment
    # ------------------------------------------------------------------
    environment: str = Field(
        default="development",
        description="Deployment environment: development | staging | production",
    )
    debug: bool = Field(default=False, description="Enable debug mode — never True in production")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------
    api_prefix: str = Field(default="/api/v1", description="URL prefix for all v1 routes")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins",
    )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    log_level: str = Field(
        default="INFO",
        description="Root log level: DEBUG | INFO | WARNING | ERROR | CRITICAL",
    )

    # ------------------------------------------------------------------
    # Derived helpers
    # ------------------------------------------------------------------
    @property
    def is_production(self) -> bool:
        """True only when running in the production environment."""
        return self.environment.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the singleton Settings instance.

    Parsed once from the ``.env`` file and cached for the process lifetime.
    Call ``get_settings.cache_clear()`` in tests to reset between test cases.
    """
    return Settings()
