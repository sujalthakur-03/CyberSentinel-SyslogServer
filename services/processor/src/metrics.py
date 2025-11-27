"""
Prometheus metrics for monitoring.
"""
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from logger import get_logger

logger = get_logger(__name__)

# Metrics
messages_consumed_total = Counter(
    "processor_messages_consumed_total",
    "Total number of messages consumed from Kafka",
    ["status"]
)

messages_processed_total = Counter(
    "processor_messages_processed_total",
    "Total number of messages processed",
    ["status"]
)

messages_indexed_total = Counter(
    "processor_messages_indexed_total",
    "Total number of messages indexed in OpenSearch",
    ["status"]
)

processing_duration_seconds = Histogram(
    "processor_processing_duration_seconds",
    "Time spent processing messages",
    ["operation"]
)

batch_size = Histogram(
    "processor_batch_size",
    "Size of processing batches",
    buckets=[10, 25, 50, 100, 250, 500, 1000]
)

enrichment_duration_seconds = Histogram(
    "processor_enrichment_duration_seconds",
    "Time spent enriching messages",
    ["enrichment_type"]
)

opensearch_errors = Counter(
    "opensearch_errors_total",
    "Total number of OpenSearch errors",
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
