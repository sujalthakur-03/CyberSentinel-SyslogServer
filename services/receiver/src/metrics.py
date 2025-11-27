"""
Prometheus metrics for monitoring.
"""
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from logger import get_logger

logger = get_logger(__name__)

# Metrics
messages_received_total = Counter(
    "syslog_messages_received_total",
    "Total number of syslog messages received",
    ["protocol", "status"]
)

messages_sent_kafka_total = Counter(
    "syslog_messages_sent_kafka_total",
    "Total number of messages sent to Kafka",
    ["status"]
)

message_size_bytes = Histogram(
    "syslog_message_size_bytes",
    "Size of received syslog messages in bytes",
    buckets=[64, 128, 256, 512, 1024, 2048, 4096, 8192]
)

processing_duration_seconds = Histogram(
    "syslog_processing_duration_seconds",
    "Time spent processing messages",
    ["operation"]
)

active_connections = Gauge(
    "syslog_active_connections",
    "Number of active connections",
    ["protocol"]
)

kafka_producer_errors = Counter(
    "kafka_producer_errors_total",
    "Total number of Kafka producer errors",
    ["error_type"]
)


def start_metrics_server(port: int) -> None:
    """
    Start Prometheus metrics HTTP server.

    Args:
        port: Port to listen on
    """
    try:
        start_http_server(port)
        logger.info("metrics_server_started", port=port)
    except Exception as e:
        logger.error("metrics_server_start_failed", error=str(e), port=port)
        raise
