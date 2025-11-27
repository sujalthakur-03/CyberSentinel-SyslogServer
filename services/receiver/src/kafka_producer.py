"""
Kafka producer with retry logic and error handling.
"""
import asyncio
import json
from typing import Optional
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from logger import get_logger
from metrics import messages_sent_kafka_total, kafka_producer_errors

logger = get_logger(__name__)


class KafkaProducerManager:
    """Manages Kafka producer lifecycle and message sending."""

    def __init__(
        self,
        bootstrap_servers: list[str],
        topic: str,
        compression_type: str = "lz4",
        batch_size: int = 16384,
        linger_ms: int = 10,
    ):
        """
        Initialize Kafka producer manager.

        Args:
            bootstrap_servers: List of Kafka broker addresses
            topic: Topic to send messages to
            compression_type: Compression algorithm (gzip, snappy, lz4, zstd)
            batch_size: Batch size in bytes
            linger_ms: Linger time in milliseconds
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.compression_type = compression_type
        self.batch_size = batch_size
        self.linger_ms = linger_ms
        self.producer: Optional[AIOKafkaProducer] = None
        self._running = False
        self._retry_delay = 5

    async def start(self) -> None:
        """Start the Kafka producer with retry logic."""
        retry_count = 0
        max_retries = 10

        while retry_count < max_retries:
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    compression_type=self.compression_type,
                    max_batch_size=self.batch_size,
                    linger_ms=self.linger_ms,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    acks="all",
                    enable_idempotence=True,
                    request_timeout_ms=30000,
                )
                await self.producer.start()
                self._running = True
                logger.info(
                    "kafka_producer_started",
                    bootstrap_servers=self.bootstrap_servers,
                    topic=self.topic,
                )
                return
            except Exception as e:
                retry_count += 1
                logger.error(
                    "kafka_producer_start_failed",
                    error=str(e),
                    retry_count=retry_count,
                    max_retries=max_retries,
                )
                kafka_producer_errors.labels(error_type="connection").inc()
                if retry_count < max_retries:
                    await asyncio.sleep(self._retry_delay)
                else:
                    raise

    async def send(self, message: dict, retries: int = 3) -> bool:
        """
        Send message to Kafka with retry logic.

        Args:
            message: Message dictionary to send
            retries: Number of retry attempts

        Returns:
            True if successful, False otherwise
        """
        if not self._running or not self.producer:
            logger.error("kafka_producer_not_started")
            messages_sent_kafka_total.labels(status="failed").inc()
            return False

        for attempt in range(retries):
            try:
                await self.producer.send_and_wait(self.topic, value=message)
                messages_sent_kafka_total.labels(status="success").inc()
                return True
            except KafkaError as e:
                logger.warning(
                    "kafka_send_failed",
                    error=str(e),
                    attempt=attempt + 1,
                    retries=retries,
                )
                kafka_producer_errors.labels(error_type=type(e).__name__).inc()
                if attempt < retries - 1:
                    await asyncio.sleep(0.1 * (2 ** attempt))
            except Exception as e:
                logger.error("kafka_send_unexpected_error", error=str(e))
                kafka_producer_errors.labels(error_type="unexpected").inc()
                break

        messages_sent_kafka_total.labels(status="failed").inc()
        return False

    async def stop(self) -> None:
        """Stop the Kafka producer gracefully."""
        if self.producer:
            try:
                await self.producer.stop()
                self._running = False
                logger.info("kafka_producer_stopped")
            except Exception as e:
                logger.error("kafka_producer_stop_failed", error=str(e))

    @property
    def is_running(self) -> bool:
        """Check if producer is running."""
        return self._running
