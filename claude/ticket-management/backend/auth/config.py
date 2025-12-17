"""
Authentication Configuration

This module defines configuration settings for the authentication service.
Reference: /backend/auth/README.md - Configuration
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """
    Authentication service settings
    Loads from environment variables with AUTH_ prefix
    """

    # ============================================================================
    # JWT Configuration
    # ============================================================================
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "your-secret-key-change-this-in-production-min-32-characters"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days

    # ============================================================================
    # Password Policy
    # ============================================================================
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # ============================================================================
    # Account Security
    # ============================================================================
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = 30
    MAX_SESSIONS_PER_USER: int = 5

    # ============================================================================
    # Email Verification
    # ============================================================================
    EMAIL_VERIFICATION_REQUIRED: bool = False
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

    # ============================================================================
    # Password Reset
    # ============================================================================
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1

    # ============================================================================
    # MFA (Multi-Factor Authentication)
    # ============================================================================
    MFA_ENABLED: bool = False
    MFA_ISSUER_NAME: str = "Ticket Management System"

    # ============================================================================
    # Database Configuration
    # ============================================================================
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/ticket_management"
    )

    # ============================================================================
    # CORS Configuration
    # ============================================================================
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    # ============================================================================
    # Rate Limiting
    # ============================================================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100  # requests per window
    RATE_LIMIT_WINDOW_SECONDS: int = 60  # 1 minute window

    # Auth endpoints specific rate limits
    LOGIN_RATE_LIMIT_REQUESTS: int = 5  # 5 login attempts
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 300  # per 5 minutes

    # ============================================================================
    # Logging Configuration
    # ============================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # ============================================================================
    # Service Configuration
    # ============================================================================
    SERVICE_NAME: str = "auth-service"
    SERVICE_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # ============================================================================
    # Environment
    # ============================================================================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"

    def validate_jwt_secret(self) -> bool:
        """Validate JWT secret key meets minimum requirements"""
        if len(self.JWT_SECRET_KEY) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters long for security"
            )
        if self.JWT_SECRET_KEY == "your-secret-key-change-this-in-production-min-32-characters":
            if self.is_production():
                raise ValueError(
                    "Default JWT_SECRET_KEY detected in production! "
                    "Please set a secure JWT_SECRET_KEY environment variable"
                )
        return True


@lru_cache()
def get_settings() -> AuthSettings:
    """
    Get cached settings instance
    Uses lru_cache to create singleton instance
    """
    settings = AuthSettings()
    # Validate critical settings
    settings.validate_jwt_secret()
    return settings


# Convenience function to get database URL
def get_database_url() -> str:
    """Get database connection URL"""
    return get_settings().DATABASE_URL


# Convenience function to check if in production
def is_production() -> bool:
    """Check if running in production environment"""
    return get_settings().is_production()
