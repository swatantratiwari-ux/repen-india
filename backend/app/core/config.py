"""
RePen India Backend — Application Configuration

Loads all settings from environment variables using Pydantic BaseSettings.
Never stores secrets in code.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """
    Central configuration loaded from .env file or environment variables.
    All secrets must be provided externally — nothing is hardcoded.
    """

    # --- Database ---
    database_url: str
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # --- JWT ---
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30  # reduced from 60 for tighter security

    # --- CORS ---
    cors_origins: str = "https://repen-india.vercel.app,http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500"

    # --- App ---
    app_env: str = "development"
    app_debug: bool = False

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Reject weak JWT secrets — must be at least 32 characters."""
        if len(v) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
            )
        return v

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings loader — instantiated once per process.
    Use as a dependency: Depends(get_settings)
    """
    return Settings()
