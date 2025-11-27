"""
Configuration management for Syslog Receiver Service.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


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

    # Receiver settings
    receiver_udp_port: int = 514
    receiver_tcp_port: int = 514
    receiver_tls_port: int = 6514
    receiver_tls_enabled: bool = True
    receiver_tls_cert_path: str = "/certs/server.crt"
    receiver_tls_key_path: str = "/certs/server.key"
    receiver_max_message_size: int = 8192
    receiver_workers: int = 4

    # Kafka settings
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_raw_logs: str = "raw-logs"
    kafka_batch_size: int = 16384
    kafka_linger_ms: int = 10
    kafka_compression_type: str = "lz4"

    # Monitoring
    prometheus_port: int = 9100

    @property
    def kafka_servers_list(self) -> list[str]:
        """Parse Kafka bootstrap servers into a list."""
        return [s.strip() for s in self.kafka_bootstrap_servers.split(",")]


# Global settings instance
settings = Settings()
