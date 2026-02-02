from __future__ import annotations
from pydantic import Field, field_validator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic-settings for validation and type safety.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database Configuration
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    database_url: str
    database_pool_size: int = Field(default=20, ge=1, le=100)
    database_max_overflow: int = Field(default=10, ge=0, le=50)
    database_pool_timeout: int = Field(default=30, ge=1, le=300)
    database_pool_recycle: int = Field(default=3600, ge=300)

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    redis_url: str
    redis_max_connections: int = Field(default=50, ge=1, le=200)

    # Crypto Configuration
    crypto_master_key: str = Field(min_length=32)

    # JWT Configuration
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    jwt_refresh_token_expire_days: int = Field(default=7, ge=1, le=90)

    # CORS Configuration
    cors_origins: list[str] = Field(default_factory=list)

    # Application Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "console"] = "json"

    # Server Configuration
    public_server_host: str = "0.0.0.0"
    public_server_port: int = 8001
    admin_server_host: str = "0.0.0.0"
    admin_server_port: int = 8002

    # Nginx Configuration
    nginx_port: int = 80

    # Rate Limiting (requests per minute)
    rate_limit_login: int = Field(default=5, ge=1, le=100)
    rate_limit_register: int = Field(default=3, ge=1, le=50)
    rate_limit_payment: int = Field(default=100, ge=1, le=1000)
    rate_limit_admin: int = Field(default=120, ge=1, le=500)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parseCorsOrigins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("database_url")
    @classmethod
    def validateDatabaseUrl(cls, v: str) -> str:
        """Validate database URL format"""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use asyncpg driver (postgresql+asyncpg://)")
        return v

    @field_validator("redis_url")
    @classmethod
    def validateRedisUrl(cls, v: str) -> str:
        """Validate Redis URL format"""
        if not v.startswith("redis://"):
            raise ValueError("REDIS_URL must start with redis://")
        return v

    @property
    def isDevelopment(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"

    @property
    def isProduction(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"

    @property
    def postgresUrl(self) -> str:
        """Build PostgreSQL URL for non-async use cases"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


# Singleton instance
settings = Settings()
