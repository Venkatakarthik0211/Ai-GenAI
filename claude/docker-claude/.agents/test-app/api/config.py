"""
Application configuration management using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables.
    """

    # Database Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://userhub:userhub123@localhost:5432/userhub",
        description="PostgreSQL database connection URL"
    )

    # JWT Configuration
    jwt_secret_key: str = Field(
        default="your-secret-key-here-change-in-production-min-32-chars-long",
        description="Secret key for JWT token generation (min 32 chars)"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )

    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins"
    )

    # Application Configuration
    app_name: str = Field(
        default="UserHub API",
        description="Application name"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    debug: bool = Field(
        default=True,
        description="Debug mode flag"
    )

    # Pagination Configuration
    default_page_size: int = Field(
        default=10,
        description="Default number of items per page"
    )
    max_page_size: int = Field(
        default=100,
        description="Maximum number of items per page"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    @validator("jwt_secret_key")
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret key length for security."""
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v

    @validator("cors_origins")
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# Global settings instance
settings = Settings()
