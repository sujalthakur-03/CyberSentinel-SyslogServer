"""
Prometheus metrics for monitoring.
"""
from prometheus_client import Counter, Histogram, start_http_server
from logger import get_logger

logger = get_logger(__name__)

# Metrics
logs_evaluated_total = Counter(
    "alerting_logs_evaluated_total",
    "Total number of logs evaluated for alerts",
)

alerts_triggered_total = Counter(
    "alerting_alerts_triggered_total",
    "Total number of alerts triggered",
    ["rule_name", "severity"]
)

alerts_sent_total = Counter(
    "alerting_alerts_sent_total",
    "Total number of alerts sent",
    ["channel", "status"]
)

alert_processing_duration_seconds = Histogram(
    "alerting_processing_duration_seconds",
    "Time spent processing alerts",
    ["operation"]
)

alert_delivery_duration_seconds = Histogram(
    "alerting_delivery_duration_seconds",
    "Time spent delivering alerts",
    ["channel"]
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
