"""
Ticket Service Configuration

This module defines configuration settings for the ticket service.
Reference: /backend/ticket/README.md - Configuration
"""

import os
from functools import lru_cache
from typing import Optional, List

from pydantic_settings import BaseSettings, SettingsConfigDict


class TicketSettings(BaseSettings):
    """
    Ticket service settings
    Loads from environment variables with TICKET_ prefix
    """

    # ============================================================================
    # Database Configuration
    # ============================================================================
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/ticket_management"
    )

    # ============================================================================
    # Auth Service Integration
    # ============================================================================
    AUTH_SERVICE_URL: str = os.getenv(
        "AUTH_SERVICE_URL",
        "http://localhost:8001"
    )
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "your-secret-key-change-this-in-production-min-32-characters"
    )
    JWT_ALGORITHM: str = "HS256"

    # ============================================================================
    # File Upload Configuration
    # ============================================================================
    UPLOAD_MAX_FILE_SIZE: int = 52428800  # 50MB in bytes
    UPLOAD_ALLOWED_EXTENSIONS: List[str] = [
        "pdf", "doc", "docx", "txt", "png", "jpg", "jpeg", "gif",
        "xls", "xlsx", "csv", "zip", "log", "json", "xml"
    ]
    UPLOAD_STORAGE_PATH: str = os.getenv(
        "UPLOAD_DIR",
        os.getenv("UPLOAD_STORAGE_PATH", "/app/uploads")
    )
    UPLOAD_STORAGE_TYPE: str = os.getenv("UPLOAD_STORAGE_TYPE", "LOCAL")  # LOCAL, S3, AZURE_BLOB

    # S3 Configuration (if using S3 storage)
    S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME")
    S3_REGION: Optional[str] = os.getenv("S3_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")

    # ============================================================================
    # Ticket Configuration
    # ============================================================================
    TICKET_NUMBER_PREFIX: str = "TKT"
    TICKET_AUTO_ASSIGN_ENABLED: bool = False
    TICKET_REOPEN_WINDOW_DAYS: int = 7  # Days after closure ticket can be reopened
    TICKET_AUTO_CLOSE_RESOLVED_DAYS: int = 3  # Days to auto-close resolved tickets
    TICKET_DEFAULT_PRIORITY: str = "P3"

    # ============================================================================
    # SLA Configuration
    # ============================================================================
    SLA_ENABLED: bool = True
    SLA_P1_RESPONSE_HOURS: int = 1
    SLA_P1_RESOLUTION_HOURS: int = 4
    SLA_P2_RESPONSE_HOURS: int = 4
    SLA_P2_RESOLUTION_HOURS: int = 24
    SLA_P3_RESPONSE_HOURS: int = 8
    SLA_P3_RESOLUTION_HOURS: int = 72
    SLA_P4_RESPONSE_HOURS: int = 24
    SLA_P4_RESOLUTION_HOURS: int = 168

    # ============================================================================
    # Notification Configuration
    # ============================================================================
    NOTIFICATIONS_ENABLED: bool = True
    EMAIL_NOTIFICATIONS_ENABLED: bool = False
    SLACK_NOTIFICATIONS_ENABLED: bool = False
    SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")

    # ============================================================================
    # Search Configuration
    # ============================================================================
    SEARCH_MIN_QUERY_LENGTH: int = 3
    SEARCH_MAX_RESULTS: int = 100

    # ============================================================================
    # Pagination Configuration
    # ============================================================================
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100

    # ============================================================================
    # CORS Configuration
    # ============================================================================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # ============================================================================
    # Rate Limiting
    # ============================================================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100  # requests per window
    RATE_LIMIT_WINDOW_SECONDS: int = 60  # 1 minute window

    # ============================================================================
    # Logging Configuration
    # ============================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # ============================================================================
    # Service Configuration
    # ============================================================================
    SERVICE_NAME: str = "ticket-service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8002
    API_V1_PREFIX: str = "/api/v1"

    # ============================================================================
    # Environment
    # ============================================================================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ============================================================================
    # Security
    # ============================================================================
    VIRUS_SCAN_ENABLED: bool = False
    VIRUS_SCAN_ON_UPLOAD: bool = False

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

    def validate_upload_path(self) -> bool:
        """Validate upload storage path exists"""
        if self.UPLOAD_STORAGE_TYPE == "LOCAL":
            os.makedirs(self.UPLOAD_STORAGE_PATH, exist_ok=True)
        return True

    def get_sla_response_hours(self, priority: str) -> int:
        """Get SLA response hours for priority"""
        sla_map = {
            "P1": self.SLA_P1_RESPONSE_HOURS,
            "P2": self.SLA_P2_RESPONSE_HOURS,
            "P3": self.SLA_P3_RESPONSE_HOURS,
            "P4": self.SLA_P4_RESPONSE_HOURS,
        }
        return sla_map.get(priority, self.SLA_P3_RESPONSE_HOURS)

    def get_sla_resolution_hours(self, priority: str) -> int:
        """Get SLA resolution hours for priority"""
        sla_map = {
            "P1": self.SLA_P1_RESOLUTION_HOURS,
            "P2": self.SLA_P2_RESOLUTION_HOURS,
            "P3": self.SLA_P3_RESOLUTION_HOURS,
            "P4": self.SLA_P4_RESOLUTION_HOURS,
        }
        return sla_map.get(priority, self.SLA_P3_RESOLUTION_HOURS)


@lru_cache()
def get_settings() -> TicketSettings:
    """
    Get cached settings instance
    Uses lru_cache to create singleton instance
    """
    settings = TicketSettings()
    # Validate upload path
    settings.validate_upload_path()
    return settings


# Convenience function to get database URL
def get_database_url() -> str:
    """Get database connection URL"""
    return get_settings().DATABASE_URL


# Convenience function to check if in production
def is_production() -> bool:
    """Check if running in production environment"""
    return get_settings().is_production()
