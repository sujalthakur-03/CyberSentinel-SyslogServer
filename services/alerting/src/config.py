"""
Configuration management for Alerting Service.
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

    # Kafka settings
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_processed_logs: str = "processed-logs"
    kafka_topic_alerts: str = "alerts"
    kafka_consumer_group_alerting: str = "alerting-group"

    # Redis settings
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # Alerting settings
    alerting_check_interval: int = 60
    alerting_smtp_host: str = "smtp.gmail.com"
    alerting_smtp_port: int = 587
    alerting_smtp_user: str = "your-email@gmail.com"
    alerting_smtp_password: str = "your-app-password"
    alerting_from_email: str = "cybersentinel@example.com"
    alerting_to_emails: str = "admin@example.com,security@example.com"
    alerting_slack_webhook_url: str = ""
    alerting_pagerduty_api_key: str = ""

    # Monitoring
    prometheus_port: int = 9103

    @property
    def kafka_servers_list(self) -> List[str]:
        """Parse Kafka bootstrap servers into a list."""
        return [s.strip() for s in self.kafka_bootstrap_servers.split(",")]

    @property
    def to_emails_list(self) -> List[str]:
        """Parse recipient emails into a list."""
        return [e.strip() for e in self.alerting_to_emails.split(",") if e.strip()]


# Global settings instance
settings = Settings()
