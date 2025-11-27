"""
Configuration management for Log Processor Service.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Kafka settings
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_raw_logs: str = "raw-logs"
    kafka_topic_processed_logs: str = "processed-logs"
    kafka_consumer_group_processor: str = "log-processor-group"
    kafka_batch_size: int = 16384
    kafka_compression_type: str = "lz4"

    # OpenSearch settings
    opensearch_host: str = "opensearch"
    opensearch_port: int = 9200
    opensearch_scheme: str = "http"
    opensearch_user: str = "admin"
    opensearch_password: str = "admin"
    opensearch_index_prefix: str = "cybersentinel-logs"
    opensearch_index_rotation: str = "daily"
    opensearch_bulk_size: int = 500
    opensearch_bulk_timeout: int = 30
    opensearch_max_retries: int = 3

    # Redis settings
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    redis_max_connections: int = 50

    # Processor settings
    processor_workers: int = 4
    processor_batch_size: int = 100
    processor_geo_ip_enabled: bool = True
    processor_threat_intel_enabled: bool = False

    # Monitoring
    prometheus_port: int = 9101

    @property
    def kafka_servers_list(self) -> list[str]:
        """Parse Kafka bootstrap servers into a list."""
        return [s.strip() for s in self.kafka_bootstrap_servers.split(",")]

    @property
    def opensearch_url(self) -> str:
        """Get OpenSearch URL."""
        return f"{self.opensearch_scheme}://{self.opensearch_host}:{self.opensearch_port}"


# Global settings instance
settings = Settings()
