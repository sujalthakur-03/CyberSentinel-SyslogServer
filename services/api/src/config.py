"""
Configuration management for API Service.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Environment
    environment: str = "production"
    log_level: str = "INFO"

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_secret_key: str = "change-this-to-a-random-secret-key-in-production"
    api_access_token_expire_minutes: int = 60
    api_cors_origins: str = "http://localhost:3000,http://localhost:8080,http://172.17.124.220:3000,http://172.17.124.220:8000"
    api_rate_limit_per_minute: int = 100

    # OpenSearch settings
    opensearch_host: str = "opensearch"
    opensearch_port: int = 9200
    opensearch_scheme: str = "http"
    opensearch_user: str = "admin"
    opensearch_password: str = "admin"
    opensearch_index_prefix: str = "cybersentinel-logs"

    # Redis settings
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    redis_max_connections: int = 50

    # Security
    jwt_secret_key: str = "change-this-jwt-secret-in-production"
    jwt_algorithm: str = "HS256"
    bcrypt_rounds: int = 12

    # Database (PostgreSQL for user management)
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "cybersentinel"
    postgres_user: str = "cybersentinel"
    postgres_password: str = "change-this-password-in-production"

    # Monitoring
    prometheus_port: int = 9102

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.api_cors_origins.split(",")]

    @property
    def opensearch_url(self) -> str:
        """Get OpenSearch URL."""
        return f"{self.opensearch_scheme}://{self.opensearch_host}:{self.opensearch_port}"

    @property
    def database_url(self) -> str:
        """Get database URL."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


# Global settings instance
settings = Settings()
